# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator


class GUIHUD:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("HUD.layout")
		self.window_combat = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
				"HUDCombat.layout")

		self.visible = False

		self.updateTooltips()

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
