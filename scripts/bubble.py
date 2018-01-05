# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
import PyCEGUI

from timeline import Timer

class SayBubble(fife.InstanceDeleteListener):
	def __init__(self, application, instance, text, time, color=""):
		fife.InstanceDeleteListener.__init__(self)
		self.application = application
		self.instance = instance
		self.timer = Timer("SayBubble" + text, time=time, action=self.destroy,
						tick_action=self.adjustPosition)
		self.application.real_timeline.addTimer(self.timer)
		self.instance.addDeleteListener(self)
		self.bubble = PyCEGUI.WindowManager.getSingleton().createWindow("TaharezLook/StaticText",
						"SayBubble-" + str(self.instance.getFifeId()))
		self.bubble.setProperty("FrameEnabled", "False")
		self.bubble.setProperty("BackgroundEnabled", "False")
		self.bubble.setProperty("MousePassThroughEnabled", "True")
		self.bubble.setProperty("HorzFormatting", "CentreAligned")
		self.shadow1 = self.bubble.clone()
		self.shadow1.setName("SayBubbleShadow1-" + str(self.instance.getFifeId()))
		self.shadow2 = self.bubble.clone()
		self.shadow2.setName("SayBubbleShadow2-" + str(self.instance.getFifeId()))
		self.shadow3 = self.bubble.clone()
		self.shadow3.setName("SayBubbleShadow3-" + str(self.instance.getFifeId()))
		self.shadow4 = self.bubble.clone()
		self.shadow4.setName("SayBubbleShadow4-" + str(self.instance.getFifeId()))
		self.application.gui.root.addChild(self.shadow1)
		self.application.gui.root.addChild(self.shadow2)
		self.application.gui.root.addChild(self.shadow3)
		self.application.gui.root.addChild(self.shadow4)
		self.application.gui.root.addChild(self.bubble)
		self.edit(text, time, color)

	def edit(self, text, time=None, color=""):
		self.text = text
		self.color = color
		self.bubble.setText(color + text)
		self.horz_extent = self.bubble.getProperty("HorzExtent")
		self.vert_extent = self.bubble.getProperty("VertExtent")
		self.bubble.setProperty("Size",
						"{{0," + self.horz_extent + "},{0," + self.vert_extent + "}}")
		self.shadow1.setText("[colour='FF000000']" + text)
		self.shadow1.setProperty("Size",
						"{{0," + self.horz_extent + "},{0," + self.vert_extent + "}}")
		self.shadow2.setText("[colour='FF000000']" + text)
		self.shadow2.setProperty("Size",
						"{{0," + self.horz_extent + "},{0," + self.vert_extent + "}}")
		self.shadow3.setText("[colour='FF000000']" + text)
		self.shadow3.setProperty("Size",
						"{{0," + self.horz_extent + "},{0," + self.vert_extent + "}}")
		self.shadow4.setText("[colour='FF000000']" + text)
		self.shadow4.setProperty("Size",
						"{{0," + self.horz_extent + "},{0," + self.vert_extent + "}}")
		if time is not None:
			self.timer.time = time
		self.adjustPosition()

	def add(self, text):
		self.edit(self.text + text, color=self.color)

	def adjustPosition(self):
		coords = self.application.camera.toScreenCoordinates(
					self.instance.getLocation().getMapCoordinates())
		self.bubble.setProperty("Position", "{{0,"
					+ str(coords.x - int(float(self.horz_extent)) // 2)
					+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 90) + "}}")
		self.shadow1.setProperty("Position", "{{0,"
					+ str(coords.x - int(float(self.horz_extent)) // 2 - 1)
					+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 91) + "}}")
		self.shadow2.setProperty("Position", "{{0,"
					+ str(coords.x - int(float(self.horz_extent)) // 2 - 1)
					+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 89) + "}}")
		self.shadow3.setProperty("Position", "{{0,"
					+ str(coords.x - int(float(self.horz_extent)) // 2 + 1)
					+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 91) + "}}")
		self.shadow4.setProperty("Position", "{{0,"
					+ str(coords.x - int(float(self.horz_extent)) // 2 + 1)
					+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 89) + "}}")

	def destroy(self, remove_listener=True):
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.bubble)
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.shadow1)
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.shadow2)
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.shadow3)
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.shadow4)
		if self.application.gui.bubbles.count(self):
			self.application.gui.bubbles.remove(self)
		if self.application.real_timeline.timers.count(self.timer):
			self.application.real_timeline.timers.remove(self.timer)
		if remove_listener:
			self.instance.removeDeleteListener(self)

	def onInstanceDeleted(self, instance):
		self.destroy(remove_listener=False)
