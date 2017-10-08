from __future__ import print_function, division
from math import pi, sqrt
from random import random
import numpy as np

class Individual(object):
	def __init__(self, id, genome, x, y, radius, energy):
		self.id = id
		self.genome = genome
		self.x = x
		self.y = y
		self.start_radius = radius
		self.radius = radius
		self.next_radius = radius
		self.energy = energy
	
	def area(self):
		return pi * self.radius**2

	def distanceTo(self, other):
		return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
	
	def winPropability(self, other, biases):
		a1, a2 = self.genome.attributes, other.genome.attributes
		n = len(a1)
		
		l1 = sum( n*a - np.dot(a2, biases[i]) for i, a in enumerate(a1) )
		l2 = sum( n*a - np.dot(a1, biases[i]) for i, a in enumerate(a2) )

		w1 = l1*self.area()
		w2 = l2*other.area()

		s = w1 + w2

		if w1 == w2: # handle s==0 case too.
			return .5

		w1 /= s
		return w1

	def combat(self, other, biases):
		""" Return who outcompetes whom. 
		"""
		p = self.winPropability(other, biases)
		return self if random() < p else other