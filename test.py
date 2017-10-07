import aabb

tree = aabb.Tree(2)
lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
lower[0] = 0
lower[1] = 0
upper[0] = 3
upper[1] = 3
print(list(tree.query(aabb.AABB(lower, upper))))

# position = aabb.DoubleVector(2)
# position[0] = 1
# position[1] = 1

# periocity = aabb.BoolVector(2)
# periocity[0] = True
# periocity[1] = True
# tree.setPeriodicity(periocity)

# tree.insertParticle(0, position, 1)
# tree.updateParticle(0, position, 2)
# # print(tree)

# lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
# lower[0] = 0
# lower[1] = 0
# upper[0] = 3
# upper[1] = 3
# print(list(tree.query(aabb.AABB(lower, upper))))
# print(AABB.lower)
# for id in tree.query(AABB):
	# print('id=',id)
