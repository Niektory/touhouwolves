# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife


class Player(object):
	def __init__(self, instance):
		self.instance = instance
		self.old_location = instance.getLocation()

	@property
	def coords(self):
		return self.instance.getLocation().getLayerCoordinates()

	@coords.setter
	def coords(self, new_coords):
		location = self.instance.getLocation()
		location.setLayerCoordinates(new_coords)
		self.instance.setLocation(location)

	def moveInstant(self, dest):
		self.old_location = self.instance.getLocation()
		if isinstance(dest, fife.Location):
			location = dest
		elif isinstance(fife.ModelCoordinate(), fife.ModelCoordinate):
			location = self.instance.getLocation()
			location.setLayerCoordinates(dest)
		self.instance.setLocation(location)
		location.getLayer().getCellCache().getCell(self.old_location.getLayerCoordinates())\
				.removeInstance(self.instance) # the deadline is making me write this shit

	def replayMove(self):
		dest = self.instance.getLocation()
		self.instance.setLocation(self.old_location)
		self.move(dest)

	def move(self, dest):
		if isinstance(dest, fife.Location):
			location = dest
		elif isinstance(fife.ModelCoordinate(), fife.ModelCoordinate):
			location = self.instance.getLocation()
			location.setLayerCoordinates(dest)
		self.instance.move("walk", location, 3)
