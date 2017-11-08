# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: nonecheck=False
# cython: cdivision=True

from __future__ import print_function, division
from libc.math cimport abs, floor, sqrt
from libc.math cimport M_PI as pi

from .utils import area_to_radius

cdef class Individual(object):
    def __init__(self, id, genome, x, y, radius, energy, growth_cost_multiplier, seed_cost_multiplier):
        self.id = id
        self.genome = genome
        self.x = x
        self.y = y
        self.start_radius = radius
        self.radius = radius
        self.next_radius = radius
        self.energy = energy
        self.next_seeds = 0
        self.alive = True

        self.grow = self.genome.grow
        self.seed = self.genome.seed
        self.seed_size = self.genome.seed_size

        self.growth_cost_multiplier = growth_cost_multiplier
        self.seed_cost_multiplier = seed_cost_multiplier

    cpdef double area(self):
        return pi * self.radius * self.radius

    cpdef void update(self):
        cdef double ind_area = self.area()

        # energy is based on it and 3/4 power rule.
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC33381/
        cdef double new_energy = ind_area**.75
        cdef double grow_energy = sqrt(new_energy * self.grow)
        cdef double seed_energy = sqrt(new_energy * self.seed)

        grow_energy /= self.growth_cost_multiplier
        seed_energy /= self.seed_cost_multiplier
        self.energy += seed_energy

        cdef double new_area = ind_area + grow_energy
        self.radius = sqrt(new_area/pi)

        # Number of seeds.
        cdef int num_seeds = int((self.energy) / self.seed_size)

        self.energy -= num_seeds * self.seed_size
        self.next_seeds = num_seeds
