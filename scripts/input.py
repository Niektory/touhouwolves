# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import division

from fife import fife

from error import LogExceptionDecorator


key_to_number = {
	fife.Key.NUM_0: 0,
	fife.Key.NUM_1: 1,
	fife.Key.NUM_2: 2,
	fife.Key.NUM_3: 3,
	fife.Key.NUM_4: 4,
	fife.Key.NUM_5: 5,
	fife.Key.NUM_6: 6,
	fife.Key.NUM_7: 7,
	fife.Key.NUM_8: 8,
	fife.Key.NUM_9: 9,
	fife.Key.KP_0: 0,
	fife.Key.KP_1: 1,
	fife.Key.KP_2: 2,
	fife.Key.KP_3: 3,
	fife.Key.KP_4: 4,
	fife.Key.KP_5: 5,
	fife.Key.KP_6: 6,
	fife.Key.KP_7: 7,
	fife.Key.KP_8: 8,
	fife.Key.KP_9: 9}


class MouseListener(fife.IMouseListener):
	def __init__(self, application):
		self.application = application
		fife.IMouseListener.__init__(self)
		self.middle_click_point = None
		self.last_click_time = 0

	@LogExceptionDecorator
	def mousePressed(self, event):
		clickpoint = fife.ScreenPoint(event.getX(), event.getY())

		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = clickpoint
			self.application.camera.detach()

		elif (event.getButton() == fife.MouseEvent.RIGHT):
			if self.application.paused:
				return

		elif (event.getButton() == fife.MouseEvent.LEFT):
			if self.application.paused:
				return

	@LogExceptionDecorator
	def mouseReleased(self, event):
		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = None

	def mouseMoved(self, event):
		pass

	def mouseEntered(self, event):
		pass

	def mouseExited(self, event):
		pass

	def mouseClicked(self, event):
		pass

	@LogExceptionDecorator
	def mouseWheelMovedUp(self, event):
		self.application.view.zoomIn()

	@LogExceptionDecorator
	def mouseWheelMovedDown(self, event):
		self.application.view.zoomOut()

	@LogExceptionDecorator
	def mouseDragged(self, event):
		if self.middle_click_point:
			self.application.view.moveCamera(
					self.middle_click_point.x - event.getX(),
					self.middle_click_point.y - event.getY())
			self.middle_click_point = fife.ScreenPoint(event.getX(), event.getY())


class KeyListener(fife.IKeyListener):
	def __init__(self, application):
		self.application = application
		fife.IKeyListener.__init__(self)
		self.alt_pressed = False

	def getHotkey(self, hotkey_name):
		try:
			return fife.Key.__dict__[self.application.settings.get("hotkeys", hotkey_name)]
		except KeyError:
			return None

	@LogExceptionDecorator
	def keyPressed(self, event):
		key_val = event.getKey().getValue()

		if key_val == fife.Key.F1:
			self.application.gui.help.home()
		elif self.application.view:
			if key_val == fife.Key.ESCAPE:
				self.application.gui.escapePressed()

			elif key_val == self.getHotkey("Pause"):
				self.application.togglePause()
			elif key_val == self.getHotkey("Turbo"):
				self.application.game_speed = 6

			elif key_val == self.getHotkey("Grid Coordinates"):
				self.application.view.toggleCoordinates()
			elif key_val == self.getHotkey("Grid Instances"):
				self.application.view.toggleGrid()
			elif key_val == self.getHotkey("Grid Blockers"):
				self.application.view.toggleCells()
			elif key_val == self.getHotkey("Fog of War"):
				self.application.view.toggleFogOfWar()

			elif key_val == self.getHotkey("Attach to PC"):
				self.application.view.attachCameraToPlayer()
			elif key_val == self.getHotkey("Zoom In"):
				self.application.view.zoomIn()
			elif key_val == self.getHotkey("Zoom Out"):
				self.application.view.zoomOut()
			elif key_val == self.getHotkey("Rotate Clockwise"):
				self.application.view.rotateClockwise()
			elif key_val == self.getHotkey("Rotate Counterclockwise"):
				self.application.view.rotateCounterclockwise()
			elif key_val == self.getHotkey("Pan Up"):
				self.application.camera.detach()
				self.application.view.camera_move_key_up = True
			elif key_val == self.getHotkey("Pan Down"):
				self.application.camera.detach()
				self.application.view.camera_move_key_down = True
			elif key_val == self.getHotkey("Pan Left"):
				self.application.camera.detach()
				self.application.view.camera_move_key_left = True
			elif key_val == self.getHotkey("Pan Right"):
				self.application.camera.detach()
				self.application.view.camera_move_key_right = True

			elif key_val == self.getHotkey("Wait"):
				self.application.world.wait()
			elif key_val == self.getHotkey("Stop Time"):
				self.application.world.stopTime()
			elif key_val == self.getHotkey("Move NE"):
				self.application.world.movePlayer(self.application.view.rotateCoords(
						fife.ModelCoordinate(1,0,0)))
			elif key_val == self.getHotkey("Move NW"):
				self.application.world.movePlayer(self.application.view.rotateCoords(
						fife.ModelCoordinate(0,-1,0)))
			elif key_val == self.getHotkey("Move SW"):
				self.application.world.movePlayer(self.application.view.rotateCoords(
						fife.ModelCoordinate(-1,0,0)))
			elif key_val == self.getHotkey("Move SE"):
				self.application.world.movePlayer(self.application.view.rotateCoords(
						fife.ModelCoordinate(0,1,0)))

	@LogExceptionDecorator
	def keyReleased(self, event):
		key_val = event.getKey().getValue()
		if self.application.view:
			if key_val == self.getHotkey("Pan Up"):
				self.application.view.camera_move_key_up = False
			elif key_val == self.getHotkey("Pan Down"):
				self.application.view.camera_move_key_down = False
			elif key_val == self.getHotkey("Pan Left"):
				self.application.view.camera_move_key_left = False
			elif key_val == self.getHotkey("Pan Right"):
				self.application.view.camera_move_key_right = False

			elif key_val == self.getHotkey("Turbo"):
				self.application.game_speed = 1
