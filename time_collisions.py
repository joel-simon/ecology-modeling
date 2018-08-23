from math import sqrt
import time
import random
# import aabb
from ecosim.collisiongrid import collision_gridx, collision_grid

worldx = collision_gridx.CollisionGrid(20, 20, 1)
world = collision_grid.CollisionGrid(20, 20, 1)

def overlaps(x1, y1, r1, x2, y2, r2):
	return sqrt((x1 - x2)**2 + (y1 - y2)**2) < r1 + r2

def collisions_brute(points):
	c = set()
	for i1, (x1, y1, r1) in points.items():
		for i2, (x2, y2, r2) in points.items():
			if i1 < i2 and overlaps(x1, y1, r1, x2, y2, r2):
				c.add((i1, i2))
	return c

def collisions_grid(points, grid):
	c = set()
	for i1, (x1, y1, r1) in points.items():
		for i2 in grid.query(x1-r1, y1-r1, x1+r1, y1+r1):
			x2, y2, r2 = points[i2]
			if i1 < i2 and overlaps(x1, y1, r1, x2, y2, r2):
				c.add((i1, i2))
	return c

def time_world(world):
	points = dict()
	start = time.time()
	random.seed(123)
	idx = 0

	for _ in range(500):
		x = random.random() * 20
		y = random.random() * 20
		r = random.random() * 2

		world.insertParticle(idx, x, y, r)
		points[idx] = (x, y, r)
		idx += 1

	for _ in range(10):

		for _ in range(5):
			kid = random.choice(list(points.keys()))
			del points[kid]
			world.removeParticle(kid)

			x = random.random() * 20
			y = random.random() * 20
			r = random.random() * 2

			world.insertParticle(idx, x, y, r)
			points[idx] = (x, y, r)
			idx += 1


		for i, (id, (x, y, r)) in enumerate(list(points.items())):
			r *= 1.1
			world.updateRadius(id, r)

	collisions = collisions_grid(points, world)
	print(len(collisions), time.time() - start)
	assert(collisions == collisions_brute(points))

time_world(worldx)
time_world(world)

# for _ in range(100):
# 	w = random.random() * 2
# 	x = random.random() * 18
# 	y = random.random() * 10
# 	# q1 = world.query(x, y, x+2, y+w)
# 	# q2 = worldx.query(x, y, x+2, y+w)

# 	q1 = world.isEmpty(x, y, w)
# 	q2 = worldx.isEmpty(x, y, w)
# 	assert q1 == q2, (q1, q2)
