from math import sqrt
import random

import aabb

tree = aabb.Tree(2)
points = []

for i in range(500):
	x = random.random()
	y = random.random()
	r = random.random() * .01
	points.append((i, x, y, r))

	position = aabb.DoubleVector(2)
	position[0] = x
	position[1] = y
	tree.insertParticle(i, position, r)

def overlaps(x1, y1, r1, x2, y2, r2):
	return sqrt((x1 - x2)**2 + (y1 - y2)**2) < r1 + r2

def collisions_brute():
	c = set()
	for i1, x1, y1, r1 in points:
		for i2, x2, y2, r2 in points:
			if i1 < i2 and overlaps(x1, y1, r1, x2, y2, r2):
				c.add((i1, i2))
	return c

def collisions_aabb():
	c = set()
	for i1, x1, y1, r1 in points:
		for i2 in tree.query(i1):
			_, x2, y2, r2 = points[i2]
			if i1 < i2 and overlaps(x1, y1, r1, x2, y2, r2):
				c.add((i1, i2))
	return c

print('n_collisions=', len(collisions_brute()))
print(collisions_brute() == collisions_aabb())

for i in range(10):
	for i in range(len(points)):
		_, x, y, r = points[i]
		r *= 1.01
		position = aabb.DoubleVector(2)
		position[0] = x
		position[1] = y
		
		points[i] = (i, x, y, r)
		
		## Uncomment these lines instead and it works
		# tree.removeParticle(i)
		# tree.insertParticle(i, position, r)
		
		tree.updateParticle(i, position, r)

	brute = collisions_brute() 

	print(len(brute), brute == collisions_aabb())