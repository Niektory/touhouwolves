# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI

from error import LogExceptionDecorator


class GUIHUD:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("HUD.layout")
		self.window_combat = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
				"HUDCombat.layout")
		self.lives = self.window.getChild("Lives")
		self.hearts = []
		for i in xrange(1,5):
			self.hearts.append(self.lives.getChild("Heart"+str(i)))
		self.bombs = self.window.getChild("Bombs")
		self.stars = []
		for i in xrange(1,4):
			self.stars.append(self.bombs.getChild("Star"+str(i)))
		self.moves = self.window.getChild("Moves")

		self.visible = False

		self.updateTooltips()

	def updateLives(self, lives_left):
		for heart in self.hearts:
			if lives_left >= 2:
				heart.setProperty("Image", "hp_1/full_image")
			elif lives_left == 1:
				heart.setProperty("Image", "hp_2/full_image")
			else:
				heart.setProperty("Image", "hp_3/full_image")
			lives_left -= 2

	def updateBombs(self, bombs_left):
		for star in self.stars:
			if bombs_left >= 2:
				star.setProperty("Image", "hp_1/full_image")
			elif bombs_left == 1:
				star.setProperty("Image", "hp_2/full_image")
			else:
				star.setProperty("Image", "hp_3/full_image")
			bombs_left -= 2

	def updateMoves(self, moves):
		self.moves.setText("MOVES\n" + str(moves))

	def updateTooltips(self):
		pass

	def getHotkeyTooltip(self, hotkey_name):
		if self.application.settings.get("hotkeys", hotkey_name):
			return " \\[" + str(self.gui.preferences.toCeguiKey(self.application.settings.get(
					"hotkeys", hotkey_name))) + "]"
		else:
			return ""

	def refresh(self):
		pass

	def show(self):
		self.window_combat.hide()
		self.visible = True
		self.window.moveToFront()
		self.refresh()

	def updateVisibility(self):
		if self.visible and not self.window_combat.isVisible():
			self.window.show()

	def showCombat(self):
		self.window.hide()
		self.window_combat.show()
		self.window_combat.moveToFront()
		self.refresh()

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()
		self.window_combat.hide()
		self.visible = False
