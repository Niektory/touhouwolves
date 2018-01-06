# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator


@LogExceptionDecorator
def propagateMouseWheel(args):
	args.window.getParent().fireEvent(PyCEGUI.Window.EventMouseWheel, args)


class GUICombatLog:
	def __init__(self, help):
		self.links = []
		self.help = help
		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("CombatLog.layout")
		self.output = self.window.getChild("TextBox")
		self.output.getChild("__auto_vscrollbar__").setEndLockEnabled(True)

	def clear(self):
		# scroll the log to the beginning
		self.output.setProperty("VertScrollPosition", "0")

		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.output.setText("")
		for link in self.links:
			if self.output.isChild(link.getID()):
				self.output.removeChild(link)

	def printMessage(self, message):
		if message == self.last_message:
			self.duplicate_count += 1
			self.messages = ("{}- {} (x{})\n".format(
						self.messages[:self.length_before_last], message, self.duplicate_count))
		else:
			self.length_before_last = len(self.messages)
			self.messages += ("- {}\n".format(message))
			self.duplicate_count = 1
		self.output.setText(self.messages)
		self.last_message = message

	def createLink(self, message, address):
		new_link = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/StaticText", "Link-{}={}".format(len(self.links) + 1, address))
		new_link.setProperty("Text", "[colour='FF00A0FF']{}".format(message))
		new_link.setProperty("FrameEnabled", "False")
		new_link.setProperty("Size", "{{{{0,{}}},{{0,{}}}}}".format(
						new_link.getProperty("HorzExtent"), new_link.getProperty("VertExtent")))
		self.output.addChild(new_link)
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseClick, self.help.linkClicked)
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseWheel, propagateMouseWheel)
		self.links.append(new_link)
		return "[window='Link-{}={}']".format(len(self.links), address)
