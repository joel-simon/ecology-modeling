from cymem.cymem cimport Pool

# Singly linked list structure.
cdef struct Entry:
    int value
    Entry *next

cdef class CollisionGrid:
    cdef Pool mem
    cdef Entry **grid
    cdef public double blocksize
    cdef public int width, height, nx, ny
    cdef public dict particles

    # Internal helpers.
    cpdef list get_block(self, int ix, int iy)
    cpdef void grid_add(self, int id, int ix, int iy) except *
    cpdef void grid_remove(self, int id, int ix, int iy) except *

    # Public methods.
    cpdef bint isEmpty(self, double x, double y, double r) except *
    cpdef void insertParticle(self, int id, double x, double y, double r) except *
    cpdef void removeParticle(self, int id) except *
    cpdef void updateRadius(self, int id, double r) except *
    cpdef set query(self, double x0, double y0, double x1, double y1)
