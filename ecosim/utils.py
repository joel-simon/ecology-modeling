from __future__ import print_function, division
from math import pi, sqrt
from random import random, randint
import numpy as np

################################################################################
""" Utils
"""
def randomly_distribute(tokens, groups):
	""" Return a random list of values with sum = tokens and length = groups.
	"""
	assert type(tokens) == int and tokens >= 0
	assert type(groups) == int and groups > 0
	
	v = sorted([ randint(0, tokens) for _ in range(groups - 1) ])
	v.append(tokens)

	result = [v[0]]
	
	for i in range(1, groups):
		result.append(v[i] - v[i-1])

	return result

def create_biases(n_attributes, power):
	# Identity on diagonals
	assert power > 0 and power <= 1

	biases = np.ones((n_attributes, n_attributes))
	
	for i in range(n_attributes):
		biases[i, 1:] = np.linspace(1-power, 1+power, n_attributes-1)
		biases[i] = np.roll(biases[i], i)

	return biases

def area_to_radius(area):
	return sqrt(area/pi)

def random_color(base=None):
	""" Returns a 3-tuple of integers in range [0, 255]
	"""
	r, g, b = randint(0,255), randint(0,255), randint(0,255)

	if base is None:
		return (r, g, b)
	else:
		r2, g2, b2 = base
		return (int((r+r2)/2), int((g+g2)/2), int((b+b2)/2))


