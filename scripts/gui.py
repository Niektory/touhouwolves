# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI
from fife import fife

from error import LogExceptionDecorator
from config.version import game_name, version
from bubble import SayBubble
from guipreferences import GUIPreferences
from guihelp import GUIHelp
from guimainmenu import GUIMainMenu, GUIGameMenu
from guitooltip import GUITooltip
from guihud import GUIHUD
from guipopupmenu import GUIPopupMenu


class GUI:
	def __init__(self, application):
		print("* Loading GUI...")
		self.application = application
		self.bubbles = []
		self.detection_bars = []

		# create the root window
		PyCEGUI.SchemeManager.getSingleton().createFromFile("TaharezLook.scheme")
		self.root = PyCEGUI.WindowManager.getSingleton().createWindow(
					"DefaultWindow", "_MasterRoot")
		self.root.setProperty("MousePassThroughEnabled", "True")
		self.context = PyCEGUI.System.getSingleton().getDefaultGUIContext()
		self.context.setRootWindow(self.root)

		# load windows from layout files and attach them to the root
		self.help = GUIHelp()
		self.root.addChild(self.help.window)
		self.preferences = GUIPreferences(self.application)
		self.root.addChild(self.preferences.window)
		self.game_menu = GUIGameMenu(self.application, self)
		self.root.addChild(self.game_menu.window)
		self.main_menu = GUIMainMenu(self.application, self)
		self.root.addChild(self.main_menu.window)
		self.hud = GUIHUD(self.application, self)
		self.root.addChild(self.hud.window)
		self.root.addChild(self.hud.window_combat)
		self.popup_menu = GUIPopupMenu(self)
		self.root.addChild(self.popup_menu.window)
		self.global_tooltip = GUITooltip()
		self.global_tooltip.shadow.setName("GlobalTooltipShadow1")
		self.global_tooltip.shadow2.setName("GlobalTooltipShadow2")
		self.global_tooltip.shadow3.setName("GlobalTooltipShadow3")
		self.global_tooltip.shadow4.setName("GlobalTooltipShadow4")
		self.global_tooltip.window.setName("GlobalTooltip")
		self.root.addChild(self.global_tooltip.shadow)
		self.root.addChild(self.global_tooltip.shadow2)
		self.root.addChild(self.global_tooltip.shadow3)
		self.root.addChild(self.global_tooltip.shadow4)
		self.root.addChild(self.global_tooltip.window)
		self.tooltip = GUITooltip()
		self.root.addChild(self.tooltip.shadow)
		self.root.addChild(self.tooltip.shadow2)
		self.root.addChild(self.tooltip.shadow3)
		self.root.addChild(self.tooltip.shadow4)
		self.root.addChild(self.tooltip.window)

		# register global sounds
		PyCEGUI.GlobalEventSet.getSingleton().subscribeEvent(
					"Window/" + PyCEGUI.PushButton.EventMouseButtonDown,
					self.buttonSound)

		# register tooltip movement
		PyCEGUI.GlobalEventSet.getSingleton().subscribeEvent(
					"Window/" + PyCEGUI.Window.EventMouseMove,
					self.moveTooltip)

		self.global_tooltip.move(0, 0)
		self.global_tooltip.printMessage(game_name + " " + version + "\n")
		self.global_tooltip.update()

		print("* GUI loaded!")

	@LogExceptionDecorator
	def buttonSound(self, args):
		if args.button != PyCEGUI.LeftButton:
			return
		if (args.window.getType()
					in ("TaharezLook/Button", "TaharezLook/ImageButton", "DragContainer",
					"TaharezLook/Checkbox", "TaharezLook/TabButton")):
			self.application.playSound("click")

	@LogExceptionDecorator
	def moveTooltip(self, args):
		# move the tooltip near the mouse cursor
		self.tooltip.move(args.position.d_x, args.position.d_y, 27, 40)

	def pump(self):
		self.tooltip.clear()
		if (self.application.gui.context.getWindowContainingMouse().getName()
					!= "_MasterRoot"):
			# cursor over the GUI, display tooltip text if any
			self.tooltip.printMessage(
					self.context.getWindowContainingMouse().getTooltipText())
		self.hud.updateVisibility()

	def pump2(self):
		self.tooltip.update()

	def sayBubble(self, instance, text, time=2000, color=""):
		for bubble in self.bubbles:
			if instance.getFifeId() == bubble.instance.getFifeId():
				bubble.edit(text, time, color)
				return
		self.bubbles.append(SayBubble(self.application, instance, text, time, color))

	def sayBubbleAdd(self, instance, text):
		for bubble in self.bubbles:
			if instance.getFifeId() == bubble.instance.getFifeId():
				bubble.add(text)
				return

	def hideAll(self):
		self.main_menu.window.hide()
		self.preferences.window.hide()
		self.game_menu.window.hide()
		self.help.window.hide()
		self.popup_menu.window.hide()
		self.hud.hide()

	def showHUD(self):
		self.hideAll()
		self.hud.show()

	def showMainMenu(self):
		self.hideAll()
		self.main_menu.show()

	def escapePressed(self):
		if self.game_menu.window.isVisible():
			self.game_menu.window.hide()
		elif self.help.window.isVisible():
			self.help.window.hide()
		elif self.preferences.window.isVisible():
			self.preferences.window.hide()
		else:
			self.game_menu.show()
