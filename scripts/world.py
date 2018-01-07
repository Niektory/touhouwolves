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
		self.bombs = 6
		self.moves_counter = 0
		self.time_stop_counter = 0

	@property
	def lives(self):
		return self._lives

	@lives.setter
	def lives(self, new_lives):
		self._lives = new_lives
		self.application.gui.hud.updateLives(self._lives)
		if self.lives <= 0:
			self.application.gui.combat_log.printMessage("GAME OVER")

	@property
	def bombs(self):
		return self._bombs

	@bombs.setter
	def bombs(self, new_bombs):
		self._bombs = new_bombs
		#self.application.gui.hud.updateBombs(self._bombs)
		self.application.gui.combat_log.printMessage("Bombs: " + str(self._bombs))

	@property
	def moves_counter(self):
		return self._moves_counter

	@moves_counter.setter
	def moves_counter(self, new_moves):
		self._moves_counter = new_moves
		self.application.gui.combat_log.printMessage("Moves: " + str(self._moves_counter))

	@property
	def animating(self):
		action = self.player.instance.getCurrentAction()
		if action and action.getId() == "walk":
			return True
		for wolf in self.wolves:
			action = wolf.instance.getCurrentAction()
			if action and action.getId() == "walk":
				return True
		return False

	@property
	def time_stop_counter(self):
		return self._time_stop_counter

	@time_stop_counter.setter
	def time_stop_counter(self, new_time):
		self._time_stop_counter = new_time
		self.application.gui.combat_log.printMessage("Time stop: " + str(self._time_stop_counter))

	def pump(self, frame_time):
		pass

	def wait(self):
		if self.animating:
			return
		self.moveEnemies()
		self.application.gui.combat_log.printMessage("Sakuya is resting...")

	def stopTime(self):
		if self.time_stop_counter:
			return
		if self.bombs < 2:
			return
		self.bombs -= 2
		self.time_stop_counter += 2

	def movePlayer(self, delta_coords):
		if self.animating:
			return
		new_coords = self.player.coords + delta_coords
		cell = self.application.maplayer.getCellCache().getCell(new_coords)
		if cell and cell.getCellType() <= 1:
			self.player.moveInstant(new_coords)
			#self.player.move(new_coords)
			self.moveEnemies()
			self.player.replayMove()
			return
		self.application.gui.combat_log.printMessage("Sakuya cannot move in that direction.")
		facing_location = self.player.instance.getLocation()
		facing_location.setLayerCoordinates(new_coords)
		self.player.instance.setFacingLocation(facing_location)
		# can't move; but maybe we can attack?
		for wolf in self.wolves:
			if facing_location == wolf.instance.getLocation():
				self.application.gui.combat_log.printMessage("Sakuya slashes wolf.")
				wolf.health -= 1
				if wolf.health <= 0:
					self.wolves.remove(wolf)
					facing_location.getLayer().deleteInstance(wolf.instance)
					self.application.gui.combat_log.printMessage("Wolf was killed.")
				self.moveEnemies()
				return

	def moveWolf(self, wolf, delta_coords):
		new_coords = wolf.coords + delta_coords
		cell = self.application.maplayer.getCellCache().getCell(new_coords)
		if cell and cell.getCellType() <= 1:
			#self.wolf.coords = new_coords # instant movement
			wolf.moveInstant(new_coords)
			return True
		#self.application.gui.combat_log.printMessage("Wolf cannot move in that direction.")
		facing_location = wolf.instance.getLocation()
		facing_location.setLayerCoordinates(new_coords)
		wolf.instance.setFacingLocation(facing_location)
		return False

	def moveWolfTo(self, wolf, location):
		cell = self.application.maplayer.getCellCache().getCell(location.getLayerCoordinates())
		if cell and cell.getCellType() <= 1:
			wolf.moveInstant(location)
			return True
		#self.application.gui.combat_log.printMessage("Wolf cannot move in that direction.")
		wolf.instance.setFacingLocation(location)
		return False

	def moveWolfTowardsPlayer(self, wolf):
		# check if the route is clear first
		route = wolf.instance.getObject().getPather().createRoute(
				wolf.instance.getLocation(), self.player.instance.getLocation(), True)
		if route.getRouteStatus() == 4:
			# route failed, aborting
			return
		elif route.getRouteStatus() == 3:
			# route solved, moving one square
			wolf.moveInstant(route.getPath()[1])

	def moveEnemies(self):
		self.moves_counter += 1
		if self.time_stop_counter:
			self.time_stop_counter -= 1
			return
		for wolf in self.wolves:
			if (wolf.instance.getLocation().getLayerDistanceTo(self.player.instance.getLocation())
					<= 1):
				self.application.gui.combat_log.printMessage("Wolf bites Sakuya. Ouch!")
				self.lives -= 1
				wolf.instance.setFacingLocation(self.player.instance.getLocation())
				wolf.instance.say("attack")
			elif self.canSeePlayer(wolf):
				self.application.gui.combat_log.printMessage("Wolf moves towards Sakuya.")
				self.moveWolfTowardsPlayer(wolf)
				wolf.instance.say("pursue")
			elif randrange(0,2) == 0:
				self.moveWolfTo(wolf, wolf.instance.getFacingLocation())
				wolf.instance.say("move straight")
			elif randrange(0,2) == 0:
				self.moveWolf(wolf, randomDirection())
				wolf.instance.say("move random")
			else:
				wolf.instance.say("idle")
		for wolf in self.wolves:
			wolf.replayMove()

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
