from __future__ import print_function
from math import pi, sqrt, hypot, floor

# import numpy as np
class CollisionGrid(object):
    """docstring for CollisionGrid"""
    def __init__(self, width, height, blocksize):
        assert width % blocksize == 0
        assert height % blocksize == 0

        self.width = width
        self.height = height
        self.blocksize = blocksize

        self.shape = (int(width / blocksize), int(height / blocksize))
        self.grid = [[set() for _ in range(self.shape[0])] for _ in range(self.shape[1])]
        self.particles = dict()

    def isEmpty(self, x, y, r):
        cx = max(0, int(floor((x-r) / self.blocksize)))
        while (cx * self.blocksize) <= min( self.width-1, x+r):

            cy = max(0, int(floor((y-r) / self.blocksize)))
            while (cy * self.blocksize) <= min( self.height-1, y+r):
                block = self.grid[cx][cy]

                for id0 in block:
                    x2, y2, r2 = self.particles[id0]
                    overlap = hypot(x - x2, y-y2) < r + r2
                    if overlap:
                        return False

                cy += 1
            cx += 1

        return True

    def insertParticle(self, id, x, y, r):
        """ Return True if add was accepted and False otherwise.
        """
        assert id not in self.particles
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height
        assert r > 0

        self.particles[id] = (x, y, r)

        cx = max(0, int(floor((x-r) / self.blocksize)))
        while (cx * self.blocksize) <= min( self.width-1, x+r):

            cy = max(0, int(floor((y-r) / self.blocksize)))
            while (cy * self.blocksize) <= min( self.height-1, y+r):

                block = self.grid[cx][cy]
                block.add(id)

                cy += 1
            cx += 1

        return True

    def removeParticle(self, id):
        x, y, r = self.particles[id]
        del self.particles[id]

        cx = max(0, int(floor((x-r) / self.blocksize)))
        while (cx * self.blocksize) <= min( self.width-1, x+r):

            cy = max(0, int(floor((y-r) / self.blocksize)))
            while (cy * self.blocksize) <= min( self.height-1, y+r):

                block = self.grid[cx][cy]
                block.remove(id)

                cy += 1
            cx += 1

    def updateRadius(self, id, r):
        """ Return True if update was accepted and False otherwise.
        """
        assert r > 0
        x, y, _ = self.particles[id]
        self.removeParticle(id)
        self.insertParticle(id, x, y, r)

        return True

    def query(self, x0, y0, x1, y1):
        seen = set()

        assert x0 < x1
        assert y0 < y1

        cx = max(0, int(floor(x0 / self.blocksize)))
        while (cx * self.blocksize) <= min( self.width-1, x1):

            cy = max(0, int(floor(y0 / self.blocksize)))
            while (cy * self.blocksize) <= min( self.height-1, y1):
                seen.update(self.grid[cx][cy])
                cy += 1

            cx += 1

        return seen
