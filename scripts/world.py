# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife

from player import Player


class World(object):
	def __init__(self, application):
		self.application = application
		for instance in self.application.maplayer.getInstances():
			if instance.getObject().getId() == "Sakuya":
				self.player = Player(instance)

	def pump(self, frame_time):
		pass

	def movePlayer(self, delta_coords):
		new_coords = self.player.coords + delta_coords
		try:
			if self.application.maplayer.getCellCache().getCell(new_coords).getCellType() <= 1:
				self.player.coords = new_coords
				return True
		except AttributeError:
			pass
		self.application.gui.combat_log.printMessage("Cannot move in that direction!")
		return False
