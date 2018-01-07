# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator

class GUIInfoDump:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("InfoDump.layout")
		self.text = self.window.getChild("Content")
		self.close_button = self.window.getChild("CloseButton")
		self.close_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.close)
		self.callback = None

	@LogExceptionDecorator
	def close(self, args=None):
		self.window.hide()
		if self.callback:
			self.callback()

	def showText(self, text, callback=None):
		self.window.show()
		self.callback = callback
		self.text.setText(text)
