from __future__ import print_function, division
from math import pi, sqrt
from random import random, randint
import numpy as np
import colorsys

################################################################################
""" Utils
"""
def area_to_radius(area):
	return sqrt(area/pi)

def random_color(base=None, saturation=.50, brightness=.95):
	""" Returns a 3-tuple of integers in range [0, 255]
	"""
	if base is None:
		r, g, b = colorsys.hsv_to_rgb(random(), saturation, brightness)
		return int(r*255), int(g*255), int(b*255)
	else:
		r2, g2, b2 = base
		return int((r+r2)/2), int((g+g2)/2), int((b+b2)/2)


