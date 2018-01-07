# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski
# helper functions for calculating grid positions etc.

from fife import fife
from math import pow, sqrt

def sign(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

def toExact(coords):
	"""Convert ModelCoordinate to ExactModelCoordinate"""
	return fife.ExactModelCoordinate(coords.x, coords.y, coords.z)

def toLayer(coords):
	"""Convert ExactModelCoordinate to ModelCoordinate"""
	return fife.ModelCoordinate(int(coords.x), int(coords.y), int(coords.z))

def distance(coords1, coords2):
	"""Calculate the real distance between 2 coordinates"""
	return sqrt(pow(coords1.x-coords2.x, 2) + pow(coords1.y-coords2.y, 2))

def angleDifference(angle1, angle2):
	"""Calculate the difference between 2 angles, ignoring sign"""
	if angle1 > angle2:
		if (angle1 - angle2) > 180:
			return (360 - (angle1 - angle2))
		else:
			return (angle1 - angle2)
	else:
		if (angle2 - angle1) > 180:
			return (360 - (angle2 - angle1))
		else:
			return (angle2 - angle1)
