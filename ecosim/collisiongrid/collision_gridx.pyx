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
    """ Fast collision detection in mass particle system.
    """
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

        cdef int i = 0
        for i in range(self.nx * self.ny):
            self.grid[i] = NULL

        self.particles = dict()

    cpdef list get_block(self, int ix, int iy):
        """ Debug function to return linked list as python list.
        """
        cdef Entry *p = self.grid[ix + iy*self.nx]
        cdef list result = []

        while p != NULL:
            result.append(p.value)
            p = p.next

        return result

    cpdef void grid_add(self, int id, int ix, int iy) except *:
        """ Helper function to prepend value to linked list.
        """
        cdef int i = ix + iy*self.nx

        if ix < 0 or ix >= self.nx:
            raise ValueError()

        if iy < 0 or iy >= self.ny:
            raise ValueError()

        cdef Entry *e = <Entry *>self.mem.alloc(1, sizeof(Entry *))

        e.value = id
        e.next = self.grid[i]

        self.grid[i] = e

    cpdef void grid_remove(self, int id, int ix, int iy) except *:
        """ Helper function to remove value from linked list.
            Assumes it only occures once.
        """
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

        # Was not found!
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

        if x < 0 or x >= self.width:
            raise ValueError()

        if y < 0 or y >= self.height:
            raise ValueError()

        if id in self.particles:
            raise ValueError()

        if r < 0:
            raise ValueError()

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

        if r < 0:
            raise ValueError()

        cdef double x, y, r0
        x, y, r0 = self.particles[id]

        cdef int cy = max(0, <int>floor((y-r) / self.blocksize))
        cdef int cy0 = max(0, <int>floor((y-r0) / self.blocksize))

        if cy == cy0:
            return

        self.removeParticle(id)
        self.insertParticle(id, x, y, r)

    cpdef set query(self, double x0, double y0, double x1, double y1):
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
