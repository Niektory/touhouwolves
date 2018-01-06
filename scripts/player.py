# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

#from fife import fife


class Player(object):
	def __init__(self, instance):
		self.instance = instance

	@property
	def coords(self):
		return self.instance.getLocation().getLayerCoordinates()

	@coords.setter
	def coords(self, new_coords):
		location = self.instance.getLocation()
		location.setLayerCoordinates(new_coords)
		self.instance.setLocation(location)

	def move(self, dest_coords):
		location = self.instance.getLocation()
		location.setLayerCoordinates(dest_coords)
		self.instance.move("walk", location, 3)
