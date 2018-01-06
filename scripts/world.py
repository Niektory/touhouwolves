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
			if instance.getObject().getId() == "Wolf":
				self.wolf = Player(instance)
		self.lives = 8

	@property
	def lives(self):
		return self._lives

	@lives.setter
	def lives(self, new_lives):
		self._lives = new_lives
		self.application.gui.hud.updateLives(self.lives)

	def pump(self, frame_time):
		pass

	def movePlayer(self, delta_coords):
		self.lives -= 1
		new_coords = self.player.coords + delta_coords
		try:
			if self.application.maplayer.getCellCache().getCell(new_coords).getCellType() <= 1:
				#self.player.coords = new_coords # instant movement
				self.player.move(new_coords)
				self.moveWolf(delta_coords)
				return True
		except AttributeError:
			pass
		self.application.gui.combat_log.printMessage("Cannot move in that direction!")
		return False

	def moveWolf(self, delta_coords):
		new_coords = self.wolf.coords + delta_coords
		try:
			if self.application.maplayer.getCellCache().getCell(new_coords).getCellType() <= 1:
				#self.player.coords = new_coords # instant movement
				self.wolf.move(new_coords)
				return True
		except AttributeError:
			pass
		self.application.gui.combat_log.printMessage("Wolf cannot move in that direction!")
		return False
