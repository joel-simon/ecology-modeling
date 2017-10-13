from __future__ import print_function, division
from math import pi, sqrt, hypot
from random import random, randint, uniform, shuffle
from collections import namedtuple

import aabb
import numpy as np
from individual import Individual
from utils import randomly_distribute, create_biases, area_to_radius

Genome = namedtuple('Genome', ['id', 'parent', 'fight', 'grow', 'seed', 
                               'seed_size', 'attributes', 'color'])

class Simulation(object):
    def __init__(self, width, height, n_start, n_attributes, bias_power,
                 seed_size_range, n_randseed, p_death, p_disturbance,
                 disturbance_power, seed_cost_multiplier):
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
        self.total_attributes = 10
        self.seed_cost_multiplier = seed_cost_multiplier
        self.max_radius = min(width, height) / 2.0
        
        ########################################################################
        self.next_ind_id = 0
        self.next_gen_id = 0
        
        ########################################################################    
        # Core objects. 
        
        self.individuals = dict()
        self.genomes = dict()
        self.biases = create_biases(self.n_attributes, self.bias_power)
        self.combat_hash = dict()
        
        ########################################################################
        # Create periodic AABB tree used for object collisions.
        
        self.tree = aabb.Tree(2, .4, 128)
        periodicity = aabb.BoolVector(2)
        periodicity[0] = True
        periodicity[1] = True
        self.tree.setPeriodicity(periodicity)
        box_size = aabb.DoubleVector(2)
        box_size[0] = self.width
        box_size[1] = self.height
        self.tree.setBoxSize(box_size)
        
        ########################################################################
        # Create intitial population.
        
        for _ in range(n_start):
            g = self.randomGenome()
            x = random() * width
            y = random() * height
            self.createIndividual(g, x, y, g.seed_size)

    def randomGenome(self):
        seed_size = uniform(*self.seed_size_range)
        fight, grow, seed = random(), random(), random()
        s = fight+grow+seed
        attributes = randomly_distribute(self.total_attributes,
                                         self.n_attributes)
        color = (randint(0,255), randint(0,255), randint(0,255))
        
        id = self.next_gen_id
        genome = Genome(id, id, fight/s, grow/s, seed/s, seed_size, attributes, color)
        self.genomes[genome.id] = genome
        self.next_gen_id += 1
        return genome

    def isEmptySpace(self, x, y, r):
        if self.tree.getNodeCount() == 0:
            return True
        
        lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
        lower[0] = x - r
        lower[1] = y - r
        upper[0] = x + r
        upper[1] = y + r
        
        for id in self.tree.query(aabb.AABB(lower, upper)):
            ind = self.individuals[id]
            d = self.distance(x, y, ind.x, ind.y)
            if d - ind.radius < r:
                return False
        
        return True

    def createIndividual(self, genome, x, y, seed_size):
        """ Returns the individuals id.
        """
        radius = area_to_radius(seed_size)

        if not self.isEmptySpace(x, y, radius):
            return None

        energy = pi * radius * radius
        ind = Individual(self.next_ind_id, genome, x, y, radius, energy)
        
        self.next_ind_id += 1
        self.individuals[ind.id] = ind

        # Add to spatial tree.
        position = aabb.DoubleVector(2)
        position[0] = x
        position[1] = y
        self.tree.insertParticle(ind.id, position, radius)

        return ind

    def destroyIndividual(self, id):
        del self.individuals[id]
        self.tree.removeParticle(id)

    def disturbRectangle(self):
        lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
        lower[0] = random()*(self.width * (1 - self.disturbance_power))
        lower[1] = random()*(self.height * (1 - self.disturbance_power))
        upper[0] = lower[0] + self.width*self.disturbance_power
        upper[1] = lower[1] + self.height*self.disturbance_power

        for id in self.tree.query(aabb.AABB(lower, upper)):
            self.destroyIndividual(id)

    def stepUpdateIndividual(self, individual, seeds):
        """ Update the individuals attributes, spatial map and create seeds. 
            We change the seed list in place.
            'seeds' is a list of tuples [(n_seeds, genome), ...]
        """
        
        ind_area = individual.area()
        
        # energy is based on it and 3.4 power rule.
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC33381/
        new_energy = ind_area**.75
        
        grow_energy = sqrt(new_energy * individual.genome.grow)
        seed_energy = sqrt(new_energy * individual.genome.seed)
        individual.energy += seed_energy

        individual.radius = area_to_radius(ind_area + grow_energy)
        individual.radius = min(self.max_radius, individual.radius)

        # Number of seeds.
        seed_cost = individual.genome.seed_size * self.seed_cost_multiplier
        num_seeds = int((individual.energy) / seed_cost)
        individual.energy -= num_seeds * seed_cost
        seeds.append((num_seeds, individual.genome))
        
        # # Update spatial map
        # self.updateIndividualSpatialTree(ind)
        # return seeds

    def updateIndividualSpatialTree(self, ind):
        position = aabb.DoubleVector(2)
        position[0] = ind.x
        position[1] = ind.y

        self.tree.updateParticle(ind.id, position, ind.radius)

    def stepSpreadSeeds(self, seeds):
        """ Spread seeds.
        """
        # print('nseeds: ', sum(s[0] for s in seeds))
        for n, genome in seeds:
            for _ in range(n):
                x, y = random() * self.width, random() * self.height
                self.createIndividual(genome, x, y, genome.seed_size)

    def distance(self, x1, y1, x2, y2):
        """ Distance function with periodic boundaries.
        """
        dx = x1 - x2
        if abs(dx) > self.width*0.5:
           dx = self.width - dx
        dy = y1 - y2
        if abs(dy) > self.height*0.5:
           dy = self.height - dy
        return hypot(dx, dy)

    def step(self):
        lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
        seeds = [(1, self.randomGenome()) for _ in range(self.n_randseed)]
        
        for individual in self.individuals.values():
            individual.blocked = False

        # Create copy of list so we can edit while we iterate randomly.
        id_list = list(self.individuals.keys())
        shuffle(id_list)
    
        for id in id_list:
            individual = self.individuals.get(id, None)
            
            # Died from combat this turn.
            if individual is None: 
                continue

            # We already lost a fight this turn, cannot grow.
            if individual.blocked: 
                continue
            
            # Chance of random death.
            if random() < self.p_death: 
                self.destroyIndividual(id)
                continue

            # Update individual list of seeds in place.
            self.stepUpdateIndividual(individual, seeds)
            
            # Query by individuals new size.
            lower[0] = individual.x - individual.radius
            lower[1] = individual.y - individual.radius
            upper[0] = individual.x + individual.radius
            upper[1] = individual.y + individual.radius
            
            for id_other in self.tree.query(aabb.AABB(lower, upper)):
                if id_other == id:
                    continue

                ind_other = self.individuals[id_other]
                dist = self.distance(individual.x, individual.y,
                                     ind_other.x, ind_other.y)
                
                # If overlapping.
                if dist > (individual.radius + ind_other.radius):
                    continue
                
                winner, loser = self.combat(individual, ind_other)

                # The loser shrinks.
                loser.blocked = True
                loser.radius = (dist - winner.radius) * .95
                if loser.radius <= loser.start_radius:
                    self.destroyIndividual(loser.id)    

                # Stop checking others if this individual lost.
                if loser is individual:
                    break

        # Udate tree with new positions.
        for id, individual in self.individuals.items():
            self.updateIndividualSpatialTree(individual)

        self.stepSpreadSeeds(seeds) 

        if random() < self.p_disturbance:
            self.disturbRectangle()
        
        # assert(self.isValid())
    
    def genomeWinProbabiliy(self, genome1, genome2):

        if genome1.id < genome2.id:
            key = (genome1.id, genome2.id)
        else:
            key = (genome2.id, genome1.id)

        if key in self.combat_hash:
            return self.combat_hash[key]

        a1, a2 = genome1.attributes, genome2.attributes
        
        n = len(a1)     
        l1 = sum( n*a - np.dot(a2, self.biases[i]) for i, a in enumerate(a1) )
        l2 = sum( n*a - np.dot(a1, self.biases[i]) for i, a in enumerate(a2) )

        self.combat_hash[key] = (l1, l2)

        return l1, l2

    def combat(self, ind1, ind2):
        """ Return who outcompetes whom. 
        """
        w1, w2 = self.genomeWinProbabiliy(ind1.genome, ind2.genome)
        w1 *= ind1.area()
        w2 *= ind2.area()
        if w1 == w2: # handle 0 case too.
            p = .5
        else:
            p = w1 / (w1 + w2)
        
        return (ind1, ind2) if random() < p else (ind2, ind1)

    def isValid(self):
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