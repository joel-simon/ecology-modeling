import unittest
from ecosim.collisiongrid.collision_gridx import CollisionGrid

class TestRandomlyDistribute(unittest.TestCase):
    def test_init(self):
        world = CollisionGrid(20, 20, 1)
        self.assertEqual(world.nx, 20)
        self.assertEqual(world.ny, 20)
        self.assertEqual(world.blocksize, 1)

    def test_grid_add(self):
        world = CollisionGrid(20, 20, 1)
        world.grid_add(0, 0, 0)
        world.grid_add(1, 0, 0)
        self.assertEqual(world.get_block(0, 0), [1, 0])

    def test_grid_remove(self):
        world = CollisionGrid(20, 20, 1)
        world.grid_add(0, 0, 0)
        world.grid_add(1, 0, 0)
        self.assertEqual(world.get_block(0, 0), [1, 0])

        world.grid_remove(0, 0, 0)
        self.assertEqual(world.get_block(0, 0), [1])

        world.grid_remove(1, 0, 0)
        self.assertEqual(world.get_block(0, 0), [])

    def test_add_particle(self):
        world = CollisionGrid(20, 20, 1)
        world.insertParticle(id=0, x=10, y=10, r=1)

    def test_remove_particle(self):
        world = CollisionGrid(20, 20, 1)
        world.insertParticle(id=0, x=10.1, y=10.1, r=.9)
        world.insertParticle(id=1, x=10.1, y=10.1, r=.9)
        world.insertParticle(id=2, x=10.1, y=10.1, r=.9)

        world.removeParticle(1)

        # for y in range(20):
        #     print([world.get_block(x, y) for x in range(20)])

        print(world.isEmpty(10, 10, 1))
        print(world.isEmpty(5, 5, 1))
        print(world.query(9, 9, 11, 11))


if __name__ == '__main__':
    unittest.main()
