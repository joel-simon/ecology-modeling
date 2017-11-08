from __future__ import print_function, division
from math import pi, sqrt, hypot
from random import random, randint, uniform, shuffle
from collections import namedtuple
import numpy as np

from .collisiongrid.collision_gridx import CollisionGrid

from .individual import Individual
from .utils import randomly_distribute, create_biases, area_to_radius, random_color

Genome = namedtuple('Genome', ['id', 'parent', 'fight', 'grow', 'seed',
                               'seed_size', 'attributes', 'color'])

class Simulation(object):
    def __init__(self, width, height, n_start, n_attributes, bias_power,
                 seed_size_range, n_randseed, p_death, p_disturbance,
                 disturbance_power, seed_cost_multiplier,
                 growth_cost_multiplier, map):

        ########################################################################
        # Configuration.

        self.width = width
        self.height = height
        self.n_start = n_start
        self.n_attributes = n_attributes
        self.bias_power = bias_power
        self.seed_size_range = seed_size_range # Starting seed size (IN AREA)
        self.n_randseed = n_randseed
        self.p_death = p_death
        self.p_disturbance = p_disturbance
        self.disturbance_power = disturbance_power
        self.seed_cost_multiplier = seed_cost_multiplier
        self.growth_cost_multiplier = growth_cost_multiplier
        self.map = map
        if self.map is not None: self.map = np.load(self.map)
        self.max_radius = min(width, height) / 2.0

        ########################################################################
        # Counters.

        self.next_ind_id = 0
        self.next_gen_id = 0
        self.step_count = 0

        ########################################################################
        # Core objects.

        self.individuals = dict()
        self.genomes = dict()
        self.biases = create_biases(self.n_attributes, self.bias_power)
        self.combat_hash = dict()
        self.world = CollisionGrid(self.width, self.height, 2)

        ########################################################################

        # if self.map is not None:
        #     map_scale = 3
        #     self.world = aabb.Tree(2, 0, np.count_nonzero(map))
        #     p = aabb.DoubleVector(2)

        #     for i, (x, y) in enumerate(zip(*np.where(self.map == 0))):
        #         p[0] = x * map_scale
        #         p[1] = self.height - (y * map_scale)
        #         self.world.insertParticle(i, p, map_scale)

        ########################################################################
        # Create intitial population.

        n_copies = 5
        for _ in range(n_start//n_copies):
            g = self.randomGenome()
            for _ in range(n_copies):
                x = random() * width
                y = random() * height
                self.createIndividual(g, x, y, g.seed_size)

        ########################################################################

    def randomGenome(self):
        seed_size = uniform(*self.seed_size_range)
        fight, grow, seed = random(), random(), random()
        s = fight+grow+seed

        attributes = np.random.rand(self.n_attributes)
        attributes /= (attributes.sum() / self.n_attributes)

        color = random_color()#saturation=1.0, brightness=.7)
        id = self.next_gen_id
        genome = Genome(id, id, fight/s, grow/s, seed/s, seed_size, attributes, color)
        self.genomes[genome.id] = genome
        self.next_gen_id += 1
        return genome

    def createIndividual(self, genome, x, y, seed_size):
        """ Returns the individuals id.
        """
        radius = area_to_radius(seed_size)

        if not self.world.isEmpty(x, y, radius):
            return None

        # for id, individual in self.individuals.items():
        #     d = self.distance(individual.x, individual.y, x, y)
        #     assert (d > individual.radius + radius), (d ,individual.radius + radius)

        ########################################################################
        # if self.map is not None:
        #     lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
        #     lower[0] = x - seed_size
        #     lower[1] = y - seed_size
        #     upper[0] = x + seed_size
        #     upper[1] = y + seed_size
        #     if len(self.world.query(aabb.AABB(lower, upper))) == 0:
        #         return None
        ########################################################################

        energy = pi * radius * radius
        ind = Individual(self.next_ind_id, genome, x, y, radius, energy, \
                                  self.growth_cost_multiplier,
                                  self.seed_cost_multiplier)

        self.next_ind_id += 1
        self.individuals[ind.id] = ind

        # Add to spatial grid.
        self.world.insertParticle(ind.id, x, y, radius)

        return ind

    def destroyIndividual(self, individual):
        individual.alive = False
        del self.individuals[individual.id]
        self.world.removeParticle(individual.id)

    def disturbRectangle(self):
        x0 = random()*(self.width * (1 - self.disturbance_power))
        y0 = random()*(self.height * (1 - self.disturbance_power))
        x1 = x0 + self.width*self.disturbance_power
        y1 = y0 + self.height*self.disturbance_power

        for id in self.world.query(x0, y0, x1, y1):
            self.destroyIndividual(self.individuals[id])

    # def stepUpdateIndividual(self, individual):
    #     """ Update the individuals attributes, spatial map and create seeds.
    #     """

    #     ind_area = individual.area()

    #     # energy is based on it and 3/4 power rule.
    #     # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC33381/
    #     new_energy = ind_area**.75

    #     grow_energy = sqrt(new_energy * individual.genome.grow) / self.growth_cost_multiplier
    #     seed_energy = sqrt(new_energy * individual.genome.seed) / self.seed_cost_multiplier
    #     individual.energy += seed_energy

    #     individual.radius = area_to_radius(ind_area + grow_energy)
    #     individual.radius = min(self.max_radius, individual.radius)

    #     # Number of seeds.
    #     seed_cost = individual.genome.seed_size
    #     num_seeds = int((individual.energy) / seed_cost)

    #     individual.energy -= num_seeds * seed_cost
    #     individual.next_seeds = num_seeds

    def stepSpreadSeeds(self):
        """ Spread seeds.
        """
        if self.step_count < 5000:
            for _ in range(self.n_randseed):
                genome = self.randomGenome()
                x, y = random() * self.width, random() * self.height
                self.createIndividual(genome, x, y, genome.seed_size)

        to_seed = []
        for individual in self.individuals.values():
            to_seed.append((individual.next_seeds, individual.genome))

        for n, genome in to_seed:
            for _ in range(n):
                x, y = random() * self.width, random() * self.height
                self.createIndividual(genome, x, y, genome.seed_size)

    def distance(self, x1, y1, x2, y2):
        """ Distance function with periodic boundaries #TODO.
        """
        dx = x1 - x2
        # if abs(dx) > self.width*0.5:
        #    dx = self.width - dx
        dy = y1 - y2
        # if abs(dy) > self.height*0.5:
        #    dy = self.height - dy
        return hypot(dx, dy)

    def updateRadius(self, individual):
        self.world.updateRadius(individual.id, individual.radius)

    def individualOverlap(self, individual):
        x0 = individual.x - individual.radius
        y0 = individual.y - individual.radius
        x1 = individual.x + individual.radius
        y1 = individual.y + individual.radius
        return self.world.query(x0, y0, x1, y1)
        # return self.world.queryCircle(individual.x, individual.y, individual.radius)

    def step(self):
        for individual in self.individuals.values():
            individual.blocked = False

        # Store in seperate list to avoid editing dict during iteration.
        to_kill = []

        for id, individual in self.individuals.items():

            # Died from combat this turn or already lost a fight
            if not individual.alive or individual.blocked:
                continue

            # Chance of random death.
            if random() < self.p_death:
                individual.alive = False
                to_kill.append(individual)
                continue

            # Update individuals.
            individual.update()

            # Query by individuals new size.
            for id_other in self.world.queryCircle(individual.x, individual.y, \
                                                            individual.radius):
                if id_other == id:
                    continue

                ind_other = self.individuals[id_other]

                if not ind_other.alive:
                    continue

                dist = self.distance(individual.x, individual.y, ind_other.x, \
                                                                ind_other.y)

                winner, loser = self.combat(individual, ind_other)

                # The loser shrinks.
                loser.blocked = True

                loser.radius = (dist - winner.radius) * .95

                killed = loser.radius <= loser.start_radius

                if killed:
                    loser.alive = False
                    to_kill.append(loser)

                # Stop checking others if this individual lost.
                if loser is individual:
                    break

                if loser is not individual and not killed:
                    self.updateRadius(loser)

            if individual.alive:
                self.updateRadius(individual)

        for individual in to_kill:
            self.destroyIndividual(individual)

        self.stepSpreadSeeds()

        if random() < self.p_disturbance:
            self.disturbRectangle()

        self.step_count += 1

    def genomeWinWeights(self, genome1, genome2):
        max_a, max_b = genome1.attributes[0], genome2.attributes[0]
        max_diff = abs(max_a - max_b)

        for a1, a2 in zip(genome1.attributes, genome2.attributes):
            if abs(a1 - a2) > max_diff:
                max_a = a1
                max_b = a2
                max_diff = abs(a1 - a2)

        return float(max_a), float(max_b)

    def combat(self, ind1, ind2):
        """ Return who outcompetes whom.
        """
        key = (ind1.genome.id, ind2.genome.id)

        if key in self.combat_hash:
            w1, w2 = self.combat_hash[key]
        else:
            w1, w2 = self.genomeWinWeights(ind1.genome, ind2.genome)
            self.combat_hash[key] = (w1, w2)

        w1 *= ind1.area()
        w2 *= ind2.area()

        if w1 == w2: # handle 0 case too.
            p = .5
        else:
            p = w1 / (w1 + w2)

        return (ind1, ind2) if random() < p else (ind2, ind1)

    def isValid(self):
        for id1, ind1 in self.individuals.items():
            assert ind1.radius == self.world.particles[id1][2]

        for id1, ind1 in self.individuals.items():
            for id2, ind2 in self.individuals.items():
                if id1 == id2:
                    continue
                d = self.distance(ind1.x, ind1.y, ind2.x, ind2.y)
                if d < ind1.radius + ind2.radius:
                    print(d, ind1.radius+ind2.radius,(ind1.x, ind1.y, ind1.radius), (ind2.x, ind2.y, ind2.radius))
                    print(id1, id2)
                    return False
        return True
