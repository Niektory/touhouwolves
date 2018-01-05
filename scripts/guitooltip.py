# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUITooltip:
	# TODO: merge the shadows with the main window; and fix the transparency
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Tooltip.layout")
		self.shadow = self.window.clone()
		self.shadow.setName("TooltipShadow")
		self.shadow2 = self.window.clone()
		self.shadow2.setName("TooltipShadow2")
		self.shadow3 = self.window.clone()
		self.shadow3.setName("TooltipShadow3")
		self.shadow4 = self.window.clone()
		self.shadow4.setName("TooltipShadow4")
		self.enabled = True
		self.prev_messages = ""
		self.clear()

	def hide(self):
		self.window.hide()
		self.shadow.hide()
		self.shadow2.hide()
		self.shadow3.hide()
		self.shadow4.hide()

	def toggle(self):
		self.enabled = not self.enabled

	def clear(self):
		self.messages = ""
		self.shadow_messages = ""

	def printMessage(self, message, color = ""):
		self.messages += (color + message)
		self.shadow_messages += (message)

	def update(self):
		if not self.enabled:
			self.hide()
			self.prev_messages = ""
			return
		if self.messages == self.prev_messages:
			return
		self.prev_messages = self.messages
		if not self.messages:
			self.hide()
			return

		self.window.show()
		self.window.setText(self.messages)
		self.window.setProperty("Size",
				"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
				self.window.getProperty("VertExtent") + "}}")
		self.shadow.show()
		self.shadow.setText("[colour='FF000000']" + self.shadow_messages)
		self.shadow.setProperty("Size",
				"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
				self.window.getProperty("VertExtent") + "}}")
		self.shadow2.show()
		self.shadow2.setText("[colour='FF000000']" + self.shadow_messages)
		self.shadow2.setProperty("Size",
				"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
				self.window.getProperty("VertExtent") + "}}")
		self.shadow3.show()
		self.shadow3.setText("[colour='FF000000']" + self.shadow_messages)
		self.shadow3.setProperty("Size",
				"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
				self.window.getProperty("VertExtent") + "}}")
		self.shadow4.show()
		self.shadow4.setText("[colour='FF000000']" + self.shadow_messages)
		self.shadow4.setProperty("Size",
				"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
				self.window.getProperty("VertExtent") + "}}")

	def move(self, x, y, x_offset=0, y_offset=0):
		self.window.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset+1), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow2.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset-1), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow3.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset+1)))
		self.shadow4.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset-1)))
