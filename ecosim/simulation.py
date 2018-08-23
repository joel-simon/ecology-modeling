from __future__ import print_function, division
from math import pi, sqrt, hypot
from random import random, randint, uniform, shuffle
from collections import namedtuple
import numpy as np

from .collisiongrid.collision_gridx import CollisionGrid

from .individual import Individual
from .utils import area_to_radius, random_color

Genome = namedtuple('Genome', ['id', 'parent', 'fight', 'grow', 'seed',
                               'seed_size', 'attributes', 'color'])

class Simulation(object):
    def __init__(self, config):
        ########################################################################
        # Configuration.

        self.width = config['width']
        self.height = config['height']
        self.n_start = config['n_start']
        self.p_death = config['p_death']
        self.n_randseed = config['n_randseed']
        # self.bias_areas = config['bias_areas']
        self.n_attributes = config['n_attributes']
        self.seed_size_range = config['seed_size_range'] # Starting seed size (IN AREA)
        self.p_disturbance = config['p_disturbance']
        self.disturbance_power = config['disturbance_power']
        self.seed_cost_multiplier = config['seed_cost_multiplier']
        self.growth_cost_multiplier = config['growth_cost_multiplier']
        self.max_radius = min(self.width, self.height) / 2.0

        self.start_grid = np.load('../data/circle.npy')
        # self.start_grid = np.load('../data/circle_gradient.npy')
        self.grid_width = self.width / self.start_grid.shape[1]
        self.grid_height = self.height / self.start_grid.shape[0]



        self.bias_map = None
        if config['bias_map']:
            self.bias_map = np.load(config['bias_map'])

        # # print(self.bias_areas)

        self.bias_vectors = []
        # for _, _, _, strength in self.bias_areas:
        #     bias_vector = np.random.rand(self.n_attributes) * strength
        #     self.bias_vectors.append(bias_vector)

        ########################################################################
        # Counters.
        self.next_ind_id = 0
        self.next_gen_id = 0
        self.step_count = 0

        ########################################################################
        # Core objects.
        self.individuals = dict()
        self.genomes = dict()
        self.world = CollisionGrid(self.width, self.height, 2)

        ########################################################################
        # Create intitial population.
        n_copies = 5
        for _ in range(self.n_start//n_copies):
            g = self.randomGenome()
            for _ in range(n_copies):
                x = random() * self.width
                y = random() * self.height
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

        row, col = int(y//self.grid_height), int(x//self.grid_width)

        prob_starting = self.start_grid[row, col]
        if random() > prob_starting:
            return None

        energy = pi * radius * radius
        has_bias = False
        attributes = genome.attributes.copy()

        if self.bias_map is not None:

            attributes *= self.bias_map[row, col]

        # for (bx, by, br, _), vector in zip(self.bias_areas, self.bias_vectors):
        #     bx *= self.width
        #     by *= self.height
        #     br *= min(self.width, self.height)

        #     if self.distance(x, y, bx, by) < radius + br:
        #         has_bias = True
        #         attributes *= vector

        ind = Individual(self.next_ind_id, genome, attributes, x, y, radius, \
                         energy, self.growth_cost_multiplier, \
                         self.seed_cost_multiplier, has_bias)

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

    def stepSpreadSeeds(self):
        """ Spread seeds.
        """
        n_randseed = int(self.n_randseed * max(0, (5000 - self.step_count) / 5000))
        # if self.step_count < 5000:
        for _ in range(n_randseed):
            genome = self.randomGenome()
            x = random() * (self.width)
            y = random() * self.height
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

                winner, loser = individual.combat(ind_other)

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

        self.step_count += 1

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
