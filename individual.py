from __future__ import print_function, division
from math import pi, hypot
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
