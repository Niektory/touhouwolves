# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator
from config.version import game_name, version

class GUIHelp:
	def __init__(self):
		self.links = []
		self.pages = dict()
		self.pages["home"] = game_name + " " + version + u"""\n\n\
			No sound - sorry!
			Default controls:
			- Arrow keys - move and attack in four directions
			- Space - rest - resting a few times in a row will heal you
			- Enter - stop time - to get out of a sticky situation
			
			This game is a derivative work (loosely) based on the Touhou Project by ZUN/Team Shanghai Alice.
			http://www16.big.or.jp/~zun/
			
			CREDITS
			Code: Niektóry
			Art: Nanako Shu
			
			An entry for the Touhou Fan Game Jam
			https://itch.io/jam/touhou-jam
			
			Kudos to the FIFE developers for the engine
			http://www.fifengine.net/"""
		self.history_back = []
		self.history_forward = []
		self.current_address = "home"
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Help.layout")
		self.text = self.window.getChild("Content")

		self.back_button = self.window.getChild("BackButton")
		self.back_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.back)
		self.forward_button = self.window.getChild("ForwardButton")
		self.forward_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.forward)
		self.home_button = self.window.getChild("HomeButton")
		self.home_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.home)
		self.close_button = self.window.getChild("CloseButton")
		self.close_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	@LogExceptionDecorator
	def linkClicked(self, args):
		address = args.window.getName()[args.window.getName().find("=")+1:]
		self.text.setText(self.pages[address])
		self.window.show()
		self.window.moveToFront()
		if self.current_address != address:
			if self.current_address:
				self.history_back.append(self.current_address)
			self.current_address = address
			self.history_forward = []
		self.updateButtons()

	@LogExceptionDecorator
	def home(self, args=None):
		self.text.setText(self.pages["home"])
		self.window.show()
		self.window.moveToFront()
		if self.current_address != "home":
			if self.current_address:
				self.history_back.append(self.current_address)
			self.current_address = "home"
			self.history_forward = []
		self.updateButtons()

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()

	def updateButtons(self):
		if len(self.history_back) > 0:
			self.back_button.setEnabled(True)
		else:
			self.back_button.setEnabled(False)
		if len(self.history_forward) > 0:
			self.forward_button.setEnabled(True)
		else:
			self.forward_button.setEnabled(False)

	@LogExceptionDecorator
	def back(self, args):
		if len(self.history_back) > 0:
			self.history_forward.append(self.current_address)
			self.current_address = self.history_back[-1]
			self.history_back.remove(self.history_back[-1])
			self.text.setText(self.pages[self.current_address])
		self.updateButtons()

	@LogExceptionDecorator
	def forward(self, args):
		if len(self.history_forward) > 0:
			self.history_back.append(self.current_address)
			self.current_address = self.history_forward[-1]
			self.history_forward.remove(self.history_forward[-1])
			self.text.setText(self.pages[self.current_address])
		self.updateButtons()

	def createPage(self, content):
		self.pages[str(len(self.pages) + 1)] = str(content)
		return str(len(self.pages))
