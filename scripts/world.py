# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from random import randrange

from player import Player
import gridhelper


def randomDirection():
	random_number = randrange(0,5)
	if random_number == 0:
		return fife.ModelCoordinate(1,0,0)
	if random_number == 1:
		return fife.ModelCoordinate(-1,0,0)
	if random_number == 2:
		return fife.ModelCoordinate(0,1,0)
	else:
		return fife.ModelCoordinate(0,-1,0)


class World(object):
	def __init__(self, application):
		self.application = application
		self.wolves = []
		for instance in self.application.maplayer.getInstances():
			if instance.getObject().getId() == "Sakuya":
				self.player = Player(instance)
			if instance.getObject().getId() == "Wolf":
				self.wolves.append(Player(instance))
		self.lives = 8

	@property
	def lives(self):
		return self._lives

	@lives.setter
	def lives(self, new_lives):
		self._lives = new_lives
		self.application.gui.hud.updateLives(self.lives)
		if self.lives <= 0:
			self.application.gui.combat_log.printMessage("GAME OVER")

	def pump(self, frame_time):
		pass

	def movePlayer(self, delta_coords):
		new_coords = self.player.coords + delta_coords
		cell = self.application.maplayer.getCellCache().getCell(new_coords)
		if cell and cell.getCellType() <= 1:
			#self.player.coords = new_coords # instant movement
			self.player.move(new_coords)
			self.moveEnemies()
			return True
		self.application.gui.combat_log.printMessage("Sakuya cannot move in that direction.")
		return False

	def moveWolf(self, wolf, delta_coords):
		new_coords = wolf.coords + delta_coords
		cell = self.application.maplayer.getCellCache().getCell(new_coords)
		if cell and cell.getCellType() <= 1:
			#self.wolf.coords = new_coords # instant movement
			wolf.move(new_coords)
			return True
		#self.application.gui.combat_log.printMessage("Wolf cannot move in that direction.")
		return False

	def moveWolfTo(self, wolf, location):
		cell = self.application.maplayer.getCellCache().getCell(location.getLayerCoordinates())
		if cell and cell.getCellType() <= 1:
			wolf.move(location)
			return True
		#self.application.gui.combat_log.printMessage("Wolf cannot move in that direction.")
		return False

	def moveEnemies(self):
		for wolf in self.wolves:
			if (wolf.instance.getLocation().getLayerDistanceTo(self.player.instance.getLocation())
					<= 1):
				self.application.gui.combat_log.printMessage("Wolf bites Sakuya. Ouch!")
				self.lives -= 1
				wolf.instance.setFacingLocation(self.player.instance.getLocation())
			elif self.canSeePlayer(wolf):
				self.application.gui.combat_log.printMessage("Wolf looks at Sakuya.")
			elif randrange(0,2) == 0:
				self.moveWolfTo(wolf, wolf.instance.getFacingLocation())
			elif randrange(0,2) == 0:
				self.moveWolf(wolf, randomDirection())

	def canSeePlayer(self, enemy):
		if (enemy.instance.getLocation().getLayerDistanceTo(self.player.instance.getLocation())
				> 5):
			# very far, can't see
			return False
		elif (enemy.instance.getLocation().getLayerDistanceTo(self.player.instance.getLocation())
				> 3):
			# within vision range, check vision angle
			angle = gridhelper.angleDifference(
					enemy.instance.getRotation(),
					fife.getAngleBetween(
						enemy.instance.getLocation(), self.player.instance.getLocation()))
			if angle > 105:
				# not in front, can't see
				return False
		# in other cases can see
		return True
