# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import division, print_function

import PyCEGUI
from fife import fife
from fife.extensions.pychan.internal import get_manager

from error import LogExceptionDecorator


class ViewLayerChangeListener(fife.LayerChangeListener):
	def onLayerChanged(self, layer, changedInstances): pass
	def onInstanceDelete(self, layer, instance): pass

	def __init__(self, view):
		super(ViewLayerChangeListener, self).__init__()
		self.view = view

	@LogExceptionDecorator
	def onInstanceCreate(self, layer, instance):
		pass


class View:
	def __init__(self, application):
		print("* Initializing view...")
		self.application = application
		self.camera = self.application.camera
		self.target_zoom = 1.0
		self.camera.setZoom(1.0)
		self.target_rotation = self.camera.getRotation()

		self.camera_move_key_up = False
		self.camera_move_key_down = False
		self.camera_move_key_left = False
		self.camera_move_key_right = False
		self.camera_move_mouse_up = False
		self.camera_move_mouse_down = False
		self.camera_move_mouse_left = False
		self.camera_move_mouse_right = False
		self.effects = []

		self.camera.setViewPort(fife.Rect(
				0, 0,
				self.application.engine.getRenderBackend().getScreenWidth(),
				self.application.engine.getRenderBackend().getScreenHeight()))

		print("  * Enabling renderers...")
		self.instance_renderer = fife.InstanceRenderer.getInstance(self.camera)
		self.instance_renderer.addIgnoreLight(["effects"])

		self.floating_text_renderer = fife.FloatingTextRenderer.getInstance(self.camera)
		textfont = get_manager().createFont(
				"fonts/rpgfont.png", 0,
				str(application.settings.get("FIFE", "FontGlyphs")));
		self.floating_text_renderer.setFont(textfont)
		self.floating_text_renderer.activateAllLayers(self.application.map)
		self.floating_text_renderer.setEnabled(True)

		self.grid_renderer = self.camera.getRenderer("GridRenderer")
		self.grid_renderer.setEnabled(False)
		self.grid_renderer.activateAllLayers(self.application.map)

		self.coordinate_renderer = fife.CoordinateRenderer.getInstance(self.camera)
		self.coordinate_renderer.setFont(textfont)
		self.coordinate_renderer.setEnabled(False)
		self.coordinate_renderer.activateAllLayers(self.application.map)

		self.cell_renderer = fife.CellRenderer.getInstance(self.camera)
		self.cell_renderer.clearActiveLayers()
		self.cell_renderer.addActiveLayer(self.application.maplayer)
		self.cell_renderer.setEnabled(True)
		self.cell_renderer.setEnabledBlocking(False)
		self.cell_renderer.setEnabledFogOfWar(False)

		self.light_renderer = fife.LightRenderer.getInstance(self.camera)
		self.light_renderer.setEnabled(True)
		self.light_renderer.clearActiveLayers()
		self.light_renderer.addActiveLayer(self.application.maplayer)

		self.layer_change_listener = ViewLayerChangeListener(self)
		self.application.maplayer.addChangeListener(self.layer_change_listener)
		print("* View initialized!")


	def toggleCoordinates(self):
		self.coordinate_renderer.setEnabled(not self.coordinate_renderer.isEnabled())

	def toggleGrid(self):
		self.grid_renderer.setEnabled(not self.grid_renderer.isEnabled())

	def toggleCells(self):
		self.cell_renderer.setEnabledBlocking(not self.cell_renderer.isEnabledBlocking())

	def zoomIn(self):
		if self.target_zoom < 1:
			self.target_zoom *= 2.0
		else:
			self.target_zoom = min(self.target_zoom + 1, 3)

	def zoomOut(self):
		if self.target_zoom <= 1:
			self.target_zoom = max(self.target_zoom / 2, 0.25)
		else:
			self.target_zoom = max(self.target_zoom - 1, 1)

	def rotateClockwise(self):
		if 180 <= (self.target_rotation - self.camera.getRotation()) % 360 <= 270:
			# don't rotate more than 180 degrees at a time
			return
		self.target_rotation = (self.target_rotation - 90) % 360

	def rotateCounterclockwise(self):
		if 90 <= (self.target_rotation - self.camera.getRotation()) % 360 <= 180:
			# don't rotate more than 180 degrees at a time
			return
		self.target_rotation = (self.target_rotation + 90) % 360

	def moveCamera(self, camera_move_x, camera_move_y):
		scr_coord = self.camera.getOrigin() + fife.ScreenPoint(camera_move_x, camera_move_y)
		coord = self.camera.toMapCoordinates(scr_coord, False)
		coord.z = 0

		# limit the camera to the current map's borders
		map_size = self.application.maplayer.getCellCache().getSize()
		if coord.x < map_size.x:
			coord.x = map_size.x
		if coord.y < map_size.y:
			coord.y = map_size.y
		if coord.x > map_size.w:
			coord.x = map_size.w
		if coord.y > map_size.h:
			coord.y = map_size.h

		loc = self.camera.getLocation()
		loc.setMapCoordinates(coord)
		self.camera.setLocation(loc)

	def animateCamera(self):
		# animate zooming
		cur_zoom = self.camera.getZoom()
		if self.target_zoom > cur_zoom:
			if self.target_zoom < cur_zoom + 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom + 0.1)
		elif self.target_zoom < cur_zoom:
			if self.target_zoom > cur_zoom - 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom - 0.1)
		# animate panning
		if self.camera_move_key_up or self.camera_move_mouse_up:
			camera_move_y = -25
		elif self.camera_move_key_down or self.camera_move_mouse_down:
			camera_move_y = 25
		else:
			camera_move_y = 0
		if self.camera_move_key_left or self.camera_move_mouse_left:
			camera_move_x = -25
		elif self.camera_move_key_right or self.camera_move_mouse_right:
			camera_move_x = 25
		else:
			camera_move_x = 0
		self.moveCamera(camera_move_x, camera_move_y)
		# animate rotation
		cur_rot = self.camera.getRotation()
		print((self.target_rotation - cur_rot) % 360)
		if self.target_rotation != cur_rot:
			if (self.target_rotation - cur_rot) % 360 < 180:
				if (self.target_rotation - cur_rot) % 360 > 5:
					self.camera.setRotation((cur_rot + 5) % 360)
				else:
					self.camera.setRotation(self.target_rotation)
			else:
				if (self.target_rotation - cur_rot) % 360 < 355:
					self.camera.setRotation((cur_rot - 5) % 360)
				else:
					self.camera.setRotation(self.target_rotation)

	def pump(self):
		self.animateCamera()
