cdef class Individual:
    cdef public int id, next_seeds, seed_size
    cdef public object genome
    cdef public double x, y, radius, start_radius, next_radius, energy, grow, \
                        seed, growth_cost_multiplier, seed_cost_multiplier
    cdef public bint alive, blocked

    cpdef double area(self)
    cpdef void update(self)
