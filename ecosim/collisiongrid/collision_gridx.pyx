# cython: boundscheck=False
# cython: wraparound=True
# cython: initializedcheck=False
# cython: nonecheck=False
# cython: cdivision=True

from __future__ import print_function
from libc.math cimport abs, floor, sqrt
from cymem.cymem cimport Pool

from math import hypot

cdef class CollisionGrid:
    def __init__(self, width, height, blocksize):
        assert width % blocksize == 0
        assert height % blocksize == 0

        self.mem = Pool()
        self.width = width
        self.height = height
        self.blocksize = blocksize

        self.nx = int(width / blocksize)
        self.ny = int(height / blocksize)

        self.grid = <Entry **>self.mem.alloc(self.nx*self.ny, sizeof(Entry *))
        # elf.grid = [[set() for _ in range(self.shape[0])] for _ in range(self.shape[1])]

        cdef int i = 0
        for i in range(self.nx * self.ny):
            self.grid[i] = NULL

        self.particles = dict()

    cpdef list get_block(self, int ix, int iy):
        cdef Entry *p = self.grid[ix + iy*self.nx]
        cdef list result = []

        while p != NULL:
            result.append(p.value)
            p = p.next

        return result

    cpdef void grid_add(self, int id, int ix, int iy) except *:
        cdef int i = ix + iy*self.nx

        assert ix >= 0 and ix < self.nx
        assert iy >= 0 and iy < self.ny

        if id in self.get_block(ix, iy):
            raise ValueError()

        cdef Entry *e = <Entry *>self.mem.alloc(1, sizeof(Entry *))

        e.value = id
        e.next = self.grid[i]

        self.grid[i] = e

    cpdef void grid_remove(self, int id, int ix, int iy) except *:
        cdef int i = ix + iy*self.nx

        cdef Entry *p = self.grid[i]

        if p == NULL:
            raise KeyError(id)
        elif p.value == id:
            self.grid[i] = p.next
            return

        while p.next != NULL:
            if p.next.value == id:
                p.next = p.next.next
                return
            p = p.next

        raise KeyError(id)

    cpdef bint isEmpty(self, double x, double y, double r) except *:
        cdef int cx, cy, id0
        cdef Entry *p
        cdef double x2, y2, r2, dx, dy

        cy = max(0, <int>floor((y-r) / self.blocksize))
        while (cy * self.blocksize) <= min( self.height-1, y+r):

            cx = max(0, <int>floor((x-r) / self.blocksize))
            while (cx * self.blocksize) <= min( self.width-1, x+r):

                p = self.grid[cx + cy*self.nx]

                while p != NULL:
                    id0 = p.value
                    x2, y2, r2 = self.particles[id0]
                    dx = x - x2
                    dy = y - y2

                    if sqrt(dx*dx + dy*dy) < r+r2:
                        return False

                    p = p.next

                cx += 1
            cy += 1

        return True

    cpdef void insertParticle(self, int id, double x, double y, double r) except *:
        cdef int cx, cy

        assert id not in self.particles
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height
        assert r > 0

        self.particles[id] = (x, y, r)

        cy = max(0, <int>floor((y-r) / self.blocksize))
        while (cy * self.blocksize) <= min( self.height-1, y+r):
            cx = max(0, <int>floor((x-r) / self.blocksize))
            while (cx * self.blocksize) <= min( self.width-1, x+r):

                self.grid_add(id, cx, cy)

                cx += 1
            cy += 1



    cpdef void removeParticle(self, int id) except *:
        cdef double x, y, r
        cdef int cx, cy

        x, y, r = self.particles[id]
        del self.particles[id]

        cy = max(0, <int>floor((y-r) / self.blocksize))
        while (cy * self.blocksize) <= min( self.height-1, y+r):

            cx = max(0, <int>floor((x-r) / self.blocksize))
            while (cx * self.blocksize) <= min( self.width-1, x+r):

                self.grid_remove(id, cx, cy)

                cx += 1
            cy += 1

    cpdef void updateRadius(self, int id, double r)  except *:
        """ Return True if update was accepted and False otherwise.
        """
        assert r > 0

        x, y, r_old = self.particles[id]

        # if abs(r/r_old) / self.blocksize < 1:
        self.removeParticle(id)
        self.insertParticle(id, x, y, r)

    cpdef set query(self, double x0, double y0, double x1, double y1):
        assert x0 < x1
        assert y0 < y1

        cdef set seen = set()
        cdef int cx, cy
        cdef Entry *p

        cy = max(0, <int>floor(y0 / self.blocksize))
        while (cy * self.blocksize) <= min( self.height-1, y1):

            cx = max(0, <int>floor(x0 / self.blocksize))
            while (cx * self.blocksize) <= min( self.width-1, x1):

                p = self.grid[cx + cy*self.nx]
                while p != NULL:
                    seen.add(p.value)
                    p = p.next

                cx += 1
            cy += 1


        return seen
