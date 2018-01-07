# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from fife.extensions.pychan.pychanbasicapplication import PychanApplicationBase
from fife.extensions.cegui.ceguibasicapplication import CEGUIApplicationBase, CEGUIEventListener
import timeit

from input import MouseListener, KeyListener
from view import View
from timeline import RealTimeline
from gui import GUI
from world import World
from config import importobjects
from config import music


class Listener(CEGUIEventListener):
	def __init__(self, application):
		super(Listener, self).__init__(application)

	def keyPressed(self, evt):
		pass


class Application(CEGUIApplicationBase, PychanApplicationBase):
	def __init__(self, settings):
		print("* Initializing application...")
		super(Application, self).__init__(settings)
		self.settings = settings
		self.model = self.engine.getModel()
		self.mapLoader = fife.MapLoader(
				self.model,
				self.engine.getVFS(),
				self.engine.getImageManager(),
				self.engine.getRenderBackend())
		self.objectLoader = fife.ObjectLoader(
				self.model,
				self.engine.getVFS(),
				self.engine.getImageManager(),
				self.engine.getAnimationManager())
		self.animationLoader = fife.AnimationLoader(
				self.engine.getVFS(),
				self.engine.getImageManager(),
				self.engine.getAnimationManager())

		self.map = None
		self.view = None
		self.change_res = False

		self.eventmanager = self.engine.getEventManager()
		self.mouselistener = MouseListener(self)
		self.keylistener = KeyListener(self)
		self.eventmanager.addMouseListenerFront(self.mouselistener)
		self.eventmanager.addKeyListenerFront(self.keylistener)
		self.soundmanager = self.engine.getSoundManager()
		self.soundmanager.init()
		self.imagemanager = self.engine.getImageManager()
		print("* Application initialized!")

		self.gui = GUI(self)
		self.real_timeline = RealTimeline()
		self.engine.getTimeManager().registerEvent(self.real_timeline)
		self.game_speed = 1

		print("* Loading objects...")
		for import_object in importobjects.import_list:
			self.loadObject(import_object)
		if self.settings.get("gameplay", "PreloadSprites", True):
			self.imagemanager.reloadAll()
		print("* Objects loaded!")

		self.sounds = {}
		self.music = None
		self.music_name = ""
		if not self.settings.get("FIFE", "PlaySounds"):
			self.soundmanager.setVolume(0.0)

		self.unloadMap()

		self.lastmem = 0
		self.last_frame_time = timeit.default_timer()

	def createListener(self):
		self._listener = Listener(self)
		return self._listener

	def playSound(self, sound):
		if sound not in self.sounds:
			self.sounds[sound] = self.soundmanager.createEmitter(
					"sfx/" + sound + ".ogg")
		self.sounds[sound].play()

	def loadObject(self, filename, pingpong = False, object_name = ""):
		if self.objectLoader.isLoadable(filename):
			self.objectLoader.load(filename)
		else:
			print("WARNING: Can't load", filename)

	def loadAtlas(self, filename):
		if self.atlasLoader.isLoadable(filename):
			self.atlasLoader.load(filename)
		else:
			print("WARNING: Can't load", filename)


	def loadMap(self, map_name):
		print("* Loading objects for map", map_name)
		for import_object in importobjects.import_by_map.get(map_name, ()):
			self.loadObject(import_object)
		if self.settings.get("gameplay", "PreloadSprites", True):
			self.imagemanager.loadAll()
		print("* Objects loaded!")
		filename = str("maps/" + map_name + ".xml")
		if self.mapLoader.isLoadable(filename):
			print("* Loading map", map_name)
			self.map = self.mapLoader.load(filename)
			self.camera = self.map.getCamera("main_camera")
			self.maplayer = self.map.getLayer("buildings_layer")
			print("* Map loaded!")
		else:
			print("WARNING: Can't load map")
		if music.music_by_map.get(map_name, self.music_name) != self.music_name:
			self.music_name = music.music_by_map[map_name]
			if self.music:
				self.music.stop()
			self.music = self.soundmanager.createEmitter(
					"music/" + self.music_name + ".ogg")
			self.music.setLooping(True)
			self.music.play()

	def unloadMap(self):
		self.real_timeline.clear()
		if self.map:
			self.model.deleteMap(self.map)
		if self.imagemanager.getMemoryUsed() > 700000000:
			self.imagemanager.freeUnreferenced()
		print("Memory used by the image manager:", "{:,}".format(self.imagemanager.getMemoryUsed()))
		self.map = None
		self.view = None
		self.world = None

	def gameOver(self):
		self.unloadMap()
		self.gui.showMainMenu()

	def newGame(self):
		print("* Starting new game...")
		self.unloadMap()
		self.loadMap("map1")
		self.unpause(True)
		self.world = World(self)
		self.view = View(self)
		self.gui.showHUD()
		self.world.movePlayer(fife.ModelCoordinate(-1,0,0))
		self.gui.info_dump.showText("Game start")
		print("* Game started!")

	def setTimeMultiplier(self, multiplier):
		self.real_timeline.multiplier = multiplier
		self.model.setTimeMultiplier(multiplier)

	def unpause(self, init=False):
		if init:
			self._paused = False
			self.force_paused = False
		self.setTimeMultiplier(self.game_speed)

	def pause(self, override=False):
		if override:
			self._paused = True
		self.setTimeMultiplier(0)

	def togglePause(self):
		if self.force_paused:
			return
		if self._paused:
			self._paused = False
			self.unpause()
		else:
			self._paused = True
			self.pause()

	@property
	def paused(self):
		return self._paused or self.force_paused

	def forcePause(self):
		gui_pause = (self.gui.game_menu.window.isVisible()
				or self.gui.preferences.window.isVisible() or self.gui.help.window.isVisible()
				or self.gui.info_dump.window.isVisible())
		if gui_pause or self._paused:
			self.pause()
		else:
			self.unpause()
		self.force_paused = gui_pause	# obsolete?

	def changeRes(self):
		self.change_res = True
		self.engine.getCursor().setNativeImageCursorEnabled(
			self.settings.get("FIFE", "NativeImageCursor", False))

	def changeRes2(self):
		self.change_res = False
		old_mode = self.engine.getRenderBackend().getCurrentScreenMode()
		new_mode = self.engine.getDeviceCaps().getNearestScreenMode(
				int(self.settings.get("FIFE", "ScreenResolution", "1024x768").split("x")[0]),
				int(self.settings.get("FIFE", "ScreenResolution", "1024x768").split("x")[1]),
				self.settings.get("FIFE", "BitsPerPixel", "0"),
				self.settings.get("FIFE", "RenderBackend", "OpenGL"),
				self.settings.get("FIFE", "FullScreen", False))
		if (old_mode.getWidth() == new_mode.getWidth()
				and old_mode.getHeight() == new_mode.getHeight()
				and old_mode.isFullScreen() == new_mode.isFullScreen()
				and self.engine.getRenderBackend().isVSyncEnabled()
					== self.settings.get("FIFE", "VSync", True)):
			return
		self.engine.getRenderBackend().setVSyncEnabled(
			self.settings.get("FIFE", "VSync", True))
		self.engine.changeScreenMode(new_mode)
		if not self.view:
			return
		self.camera.setViewPort(fife.Rect(0, 0,
			self.engine.getRenderBackend().getScreenWidth(),
			self.engine.getRenderBackend().getScreenHeight()))
		self.camera.refresh()

	def _pump(self):
		current_frame_time = timeit.default_timer()
		self.last_frame_time = current_frame_time
		if self.change_res:
			self.changeRes2()
			return
		if self.imagemanager.getMemoryUsed() != self.lastmem:
			print("Memory used by the image manager:", "{:,}".format(
															self.imagemanager.getMemoryUsed()))
			self.lastmem = self.imagemanager.getMemoryUsed()
		self.gui.pump()
		if self.view:
			self.forcePause()
			if self.world and not self.paused:
				self.world.pump(self.real_timeline.last_frame_time)
		if self.view:
			self.view.pump()
		self.gui.pump2()
		if self._listener.quitrequested:
			self.quit()
