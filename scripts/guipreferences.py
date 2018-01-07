# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import division, print_function

import PyCEGUI
from fife import fife

from error import LogExceptionDecorator


class GUIPreferences:
	def __init__(self, application):
		self.application = application
		self.initKeyMap()

		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Preferences.layout")

		# add tabs for video, audio and controls
		self.tab_control = self.window.getChild("TabControl")
		self.page_gameplay = self.window.getChild("TabPaneGameplay")
		self.page_video = self.window.getChild("TabPaneVideo")
		self.page_audio = self.window.getChild("TabPaneAudio")
		self.page_controls = self.window.getChild("TabPaneControls")
		self.page_controls_scrollable = self.page_controls.getChild("ScrollablePane")
		self.tab_control.addTab(self.page_gameplay)
		self.tab_control.addTab(self.page_video)
		self.tab_control.addTab(self.page_audio)
		self.tab_control.addTab(self.page_controls)

		# gameplay controls
		self.time_acceleration_edit = self.page_gameplay.getChild("TimeAccelerationEdit")
		self.preload_sprites_checkbox = self.page_gameplay.getChild("PreloadSpritesCheckbox")

		# video and audio controls
		self.resolution_list = self.page_video.getChild("Resolutions")
		self.fullscreen_checkbox = self.page_video.getChild("Fullscreen")
		self.vsync_checkbox = self.page_video.getChild("VSync")
		self.native_cursor_checkbox = self.page_video.getChild("NativeCursor")
		self.enable_sound_checkbox = self.page_audio.getChild("Enable")
		self.volume_slider = self.page_audio.getChild("VolumeSlider")

		# hotkey controls
		self.hotkey_labels = []
		self.hotkey_edits = []
		self.hotkey_actions = [
			"-- Debug --", "Grid Coordinates", "Grid Instances", "Grid Blockers", "Turbo",
			"Fog of War",
			"-- Camera Control --",
			"Pan Up", "Pan Down", "Pan Left", "Pan Right", "Zoom In", "Zoom Out",
			"Rotate Clockwise", "Rotate Counterclockwise", "Attach to PC",
			"-- Game Control --", "Pause",
			"-- Player Control --",
			"Move NE", "Move NW", "Move SW", "Move SE", "Wait", "Stop Time"]
		vert_pos = 10
		for action in self.hotkey_actions:
			new_hotkey_label = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Label", "HotkeyLabel-" + action)
			new_hotkey_label.setProperty("Text", action)
			new_hotkey_label.setProperty("Position", "{{0,10},{0," + str(vert_pos) + "}}")
			new_hotkey_label.setProperty("VertFormatting", "TopAligned")
			new_hotkey_label.setProperty("Disabled", "True")

			if action[1] == "-":
				# just a separator label
				new_hotkey_label.setProperty("Size", "{{1,-20},{0,20}}")
				new_hotkey_label.setProperty("HorzFormatting", "CentreAligned")
			else:
				new_hotkey_label.setProperty("Size", "{{0,140},{0,20}}")
				new_hotkey_label.setProperty("HorzFormatting", "RightAligned")

				new_hotkey_edit = PyCEGUI.WindowManager.getSingleton().createWindow(
						"TaharezLook/Editbox", "HotkeyEdit-" + action)
				new_hotkey_edit.setProperty("Size", "{{1,-170},{0,28}}")
				new_hotkey_edit.setProperty("Position", "{{0,160},{0," + str(vert_pos - 7) + "}}")
				new_hotkey_edit.setProperty("TextParsingEnabled", "False")
				new_hotkey_edit.setProperty("MouseInputPropagationEnabled", "True")

				new_hotkey_edit.subscribeEvent(PyCEGUI.Editbox.EventKeyDown, self.hotkeyPressed)
				new_hotkey_edit.subscribeEvent(PyCEGUI.Editbox.EventKeyUp, lambda args: True)
				new_hotkey_edit.subscribeEvent(
								PyCEGUI.Editbox.EventCharacterKey, lambda args: True)

				self.page_controls_scrollable.addChild(new_hotkey_edit)
				self.hotkey_edits.append(new_hotkey_edit)
				self.hotkey_labels.append(new_hotkey_label)

			self.page_controls_scrollable.addChild(new_hotkey_label)
			vert_pos += 30

		self.OK_button = self.window.getChild("OKButton")
		self.OK_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.savePreferences)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	@LogExceptionDecorator
	def savePreferences(self, args):
		if self.enable_sound_checkbox.isSelected():
			self.application.soundmanager.setVolume(
						self.volume_slider.getScrollPosition() / 10)
		else:
			self.application.soundmanager.setVolume(0.0)
		self.application.settings.set("gameplay", "TimeAcceleration",
					int(self.time_acceleration_edit.getText()))
		self.application.settings.set("gameplay", "PreloadSprites",
					self.preload_sprites_checkbox.isSelected())

		if self.resolution_list.getFirstSelectedItem():
			self.application.settings.set("FIFE", "ScreenResolution",
					self.resolution_list.getFirstSelectedItem().getText())
		self.application.settings.set("FIFE", "FullScreen",
					self.fullscreen_checkbox.isSelected())
		self.application.settings.set("FIFE", "VSync",
					self.vsync_checkbox.isSelected())
		self.application.settings.set("FIFE", "NativeImageCursor",
					self.native_cursor_checkbox.isSelected())
		self.application.settings.set("FIFE", "PlaySounds",
					self.enable_sound_checkbox.isSelected())
		self.application.settings.set("FIFE", "InitialVolume",
					self.volume_slider.getScrollPosition())
		for label, edit in zip(self.hotkey_labels, self.hotkey_edits):
			self.application.settings.set("hotkeys", label.getText(),
					edit.getProperty("HiddenData"))
		self.application.settings.saveSettings()
		self.application.gui.hud.updateTooltips()
		self.application.changeRes()
		self.window.hide()

	@LogExceptionDecorator
	def show(self, args=None):
		settings = self.application.settings	# shortcut

		# load gameplay settings
		self.time_acceleration_edit.setText(
				str(settings.get("gameplay", "TimeAcceleration", 1)))
		self.preload_sprites_checkbox.setSelected(
				settings.get("gameplay", "PreloadSprites", True))

		# load video and audio settings
		self.resolution_list.resetList()
		self.resolution_items = []
		for resolution in self.application.settings._resolutions:
			self.resolution_items.append(PyCEGUI.ListboxTextItem(resolution))
			self.resolution_items[-1].setAutoDeleted(False)
			self.resolution_items[-1].setSelectionBrushImage(
					"TaharezLook/MultiListSelectionBrush")
			self.resolution_items[-1].setSelectionColours(PyCEGUI.Colour(0.33, 0.295, 0.244))
			self.resolution_items[-1].setTextColours(PyCEGUI.Colour(0.98, 0.886, 0.733))
			self.resolution_list.addItem(self.resolution_items[-1])
			if resolution == settings.get("FIFE", "ScreenResolution", "1024x768"):
				self.resolution_list.setItemSelectState(self.resolution_items[-1], True)
		self.fullscreen_checkbox.setSelected(settings.get("FIFE", "FullScreen", False))
		self.vsync_checkbox.setSelected(settings.get("FIFE", "VSync", True))
		self.native_cursor_checkbox.setSelected(settings.get("FIFE", "NativeImageCursor", False))
		self.enable_sound_checkbox.setSelected(settings.get("FIFE", "PlaySounds", True))
		self.volume_slider.setScrollPosition(settings.get("FIFE", "InitialVolume", 10.0))

		# load hotkeys
		for action in self.hotkey_actions:
			if action[1] == "-":
				# skip separator labels
				continue
			hotkey_edit = self.page_controls_scrollable.getChild("HotkeyEdit-" + action)
			fife_key = settings.get("hotkeys", action)
			try:
				cegui_key = self.toCeguiKey(fife_key)
			except KeyError:
				hotkey_edit.setProperty("Text", "")
				hotkey_edit.setProperty("HiddenData", "")
			else:
				hotkey_edit.setProperty("Text", str(cegui_key))
				hotkey_edit.setProperty("HiddenData", str(fife_key))

		self.window.show()
		self.window.moveToFront()

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()

	@LogExceptionDecorator
	def hotkeyPressed(self, args):
		for edit in self.hotkey_edits:
			if str(args.scancode) == edit.getText():
				return True
		if args.scancode in [PyCEGUI.Key.Escape, PyCEGUI.Key.F1]:
			args.window.setText("")
			args.window.setProperty("HiddenData", "")
		else:
			args.window.setText(str(args.scancode))
			args.window.setProperty("HiddenData", str(self.toFifeKey(args.scancode)))
		args.window.deactivate()
		return True

	def toFifeKey(self, key):
		return self.r_keymap[key]

	def toCeguiKey(self, key):
		return self.keymap[key]

	def addKey(self, fife_key, cegui_key):
		try:
			fife.Key.__dict__[fife_key]
		except KeyError:
			print("Invalid FIFE key: {}".format(fife_key))
			return
		self.keymap[fife_key] = cegui_key
		self.r_keymap[cegui_key] = fife_key

	def initKeyMap(self):
		self.keymap = {}
		self.r_keymap = {}

		self.addKey("NUM_1", PyCEGUI.Key.One)
		self.addKey("NUM_2", PyCEGUI.Key.Two)
		self.addKey("NUM_3", PyCEGUI.Key.Three)
		self.addKey("NUM_4", PyCEGUI.Key.Four)
		self.addKey("NUM_5", PyCEGUI.Key.Five)
		self.addKey("NUM_6", PyCEGUI.Key.Six)
		self.addKey("NUM_7", PyCEGUI.Key.Seven)
		self.addKey("NUM_8", PyCEGUI.Key.Eight)
		self.addKey("NUM_9", PyCEGUI.Key.Nine)
		self.addKey("NUM_0", PyCEGUI.Key.Zero)

		self.addKey("Q", PyCEGUI.Key.Q)
		self.addKey("W", PyCEGUI.Key.W)
		self.addKey("E", PyCEGUI.Key.E)
		self.addKey("R", PyCEGUI.Key.R)
		self.addKey("T", PyCEGUI.Key.T)
		self.addKey("Y", PyCEGUI.Key.Y)
		self.addKey("U", PyCEGUI.Key.U)
		self.addKey("I", PyCEGUI.Key.I)
		self.addKey("O", PyCEGUI.Key.O)
		self.addKey("P", PyCEGUI.Key.P)
		self.addKey("A", PyCEGUI.Key.A)
		self.addKey("S", PyCEGUI.Key.S)
		self.addKey("D", PyCEGUI.Key.D)
		self.addKey("F", PyCEGUI.Key.F)
		self.addKey("G", PyCEGUI.Key.G)
		self.addKey("H", PyCEGUI.Key.H)
		self.addKey("J", PyCEGUI.Key.J)
		self.addKey("K", PyCEGUI.Key.K)
		self.addKey("L", PyCEGUI.Key.L)
		self.addKey("Z", PyCEGUI.Key.Z)
		self.addKey("X", PyCEGUI.Key.X)
		self.addKey("C", PyCEGUI.Key.C)
		self.addKey("V", PyCEGUI.Key.V)
		self.addKey("B", PyCEGUI.Key.B)
		self.addKey("N", PyCEGUI.Key.N)
		self.addKey("M", PyCEGUI.Key.M)

		self.addKey("COMMA", PyCEGUI.Key.Comma)
		self.addKey("PERIOD", PyCEGUI.Key.Period)
		self.addKey("SLASH", PyCEGUI.Key.Slash)
		self.addKey("BACKSLASH", PyCEGUI.Key.Backslash)
		self.addKey("MINUS", PyCEGUI.Key.Minus)
		self.addKey("EQUALS", PyCEGUI.Key.Equals)
		self.addKey("SEMICOLON", PyCEGUI.Key.Semicolon)
		self.addKey("COLON", PyCEGUI.Key.Colon)
		self.addKey("LEFTBRACKET", PyCEGUI.Key.LeftBracket)
		self.addKey("RIGHTBRACKET", PyCEGUI.Key.RightBracket)
		self.addKey("QUOTE", PyCEGUI.Key.Apostrophe)
		self.addKey("BACKQUOTE", PyCEGUI.Key.Grave)
		self.addKey("AT", PyCEGUI.Key.At)
		self.addKey("UNDERSCORE", PyCEGUI.Key.Underline)

		self.addKey("ENTER", PyCEGUI.Key.Return)
		self.addKey("SPACE", PyCEGUI.Key.Space)
		self.addKey("BACKSPACE", PyCEGUI.Key.Backspace)
		self.addKey("TAB", PyCEGUI.Key.Tab)

		self.addKey("ESCAPE", PyCEGUI.Key.Escape)
		self.addKey("PAUSE", PyCEGUI.Key.Pause)
		self.addKey("SYS_REQ", PyCEGUI.Key.SysRq)
		self.addKey("POWER", PyCEGUI.Key.Power)
		self.addKey("SLEEP", PyCEGUI.Key.Sleep)

		self.addKey("CALCULATOR", PyCEGUI.Key.Calculator)
		self.addKey("MAIL", PyCEGUI.Key.Mail)
		self.addKey("COMPUTER", PyCEGUI.Key.MyComputer)
		self.addKey("MEDIASELECT", PyCEGUI.Key.MediaSelect)
		self.addKey("STOP", PyCEGUI.Key.Stop)

		self.addKey("AUDIO_PLAY", PyCEGUI.Key.PlayPause)
		self.addKey("AUDIO_STOP", PyCEGUI.Key.MediaStop)
		self.addKey("AUDIO_PREV", PyCEGUI.Key.PrevTrack)
		self.addKey("AUDIO_NEXT", PyCEGUI.Key.NextTrack)
		self.addKey("MUTE", PyCEGUI.Key.Mute)
		self.addKey("VOLUME_UP", PyCEGUI.Key.VolumeUp)
		self.addKey("VOLUME_DOWN", PyCEGUI.Key.VolumeDown)

		self.addKey("AC_BACK", PyCEGUI.Key.WebBack)
		self.addKey("AC_FORWARD", PyCEGUI.Key.WebForward)
		self.addKey("AC_HOME", PyCEGUI.Key.WebHome)
		self.addKey("AC_BOOKMARKS", PyCEGUI.Key.WebFavorites)
		self.addKey("AC_SEARCH", PyCEGUI.Key.WebSearch)
		self.addKey("AC_REFRESH", PyCEGUI.Key.WebRefresh)
		self.addKey("AC_STOP", PyCEGUI.Key.WebStop)

		self.addKey("NUM_LOCK", PyCEGUI.Key.NumLock)
		self.addKey("SCROLL_LOCK", PyCEGUI.Key.ScrollLock)
		self.addKey("CAPS_LOCK", PyCEGUI.Key.Capital)

		self.addKey("F1", PyCEGUI.Key.F1)
		self.addKey("F2", PyCEGUI.Key.F2)
		self.addKey("F3", PyCEGUI.Key.F3)
		self.addKey("F4", PyCEGUI.Key.F4)
		self.addKey("F5", PyCEGUI.Key.F5)
		self.addKey("F6", PyCEGUI.Key.F6)
		self.addKey("F7", PyCEGUI.Key.F7)
		self.addKey("F8", PyCEGUI.Key.F8)
		self.addKey("F9", PyCEGUI.Key.F9)
		self.addKey("F10", PyCEGUI.Key.F10)
		self.addKey("F11", PyCEGUI.Key.F11)
		self.addKey("F12", PyCEGUI.Key.F12)
		self.addKey("F13", PyCEGUI.Key.F13)
		self.addKey("F14", PyCEGUI.Key.F14)
		self.addKey("F15", PyCEGUI.Key.F15)

		self.addKey("LEFT_CONTROL", PyCEGUI.Key.LeftControl)
		self.addKey("LEFT_ALT", PyCEGUI.Key.LeftAlt)
		self.addKey("LEFT_SHIFT", PyCEGUI.Key.LeftShift)
		self.addKey("LEFT_SUPER", PyCEGUI.Key.LeftWindows)
		self.addKey("RIGHT_CONTROL", PyCEGUI.Key.RightControl)
		self.addKey("RIGHT_ALT", PyCEGUI.Key.RightAlt)
		self.addKey("RIGHT_SHIFT", PyCEGUI.Key.RightShift)
		self.addKey("RIGHT_SUPER", PyCEGUI.Key.RightWindows)
		self.addKey("MENU", PyCEGUI.Key.AppMenu)

		self.addKey("KP_0", PyCEGUI.Key.Numpad0)
		self.addKey("KP_1", PyCEGUI.Key.Numpad1)
		self.addKey("KP_2", PyCEGUI.Key.Numpad2)
		self.addKey("KP_3", PyCEGUI.Key.Numpad3)
		self.addKey("KP_4", PyCEGUI.Key.Numpad4)
		self.addKey("KP_5", PyCEGUI.Key.Numpad5)
		self.addKey("KP_6", PyCEGUI.Key.Numpad6)
		self.addKey("KP_7", PyCEGUI.Key.Numpad7)
		self.addKey("KP_8", PyCEGUI.Key.Numpad8)
		self.addKey("KP_9", PyCEGUI.Key.Numpad9)
		self.addKey("KP_PERIOD", PyCEGUI.Key.Decimal)
		self.addKey("KP_PLUS", PyCEGUI.Key.Add)
		self.addKey("KP_MINUS", PyCEGUI.Key.Subtract)
		self.addKey("KP_MULTIPLY", PyCEGUI.Key.Multiply)
		self.addKey("KP_DIVIDE", PyCEGUI.Key.Divide)
		self.addKey("KP_ENTER", PyCEGUI.Key.NumpadEnter)
		self.addKey("KP_COMMA", PyCEGUI.Key.NumpadComma)
		self.addKey("KP_EQUALS", PyCEGUI.Key.NumpadEquals)

		self.addKey("UP", PyCEGUI.Key.ArrowUp)
		self.addKey("LEFT", PyCEGUI.Key.ArrowLeft)
		self.addKey("RIGHT", PyCEGUI.Key.ArrowRight)
		self.addKey("DOWN", PyCEGUI.Key.ArrowDown)

		self.addKey("HOME", PyCEGUI.Key.Home)
		self.addKey("END", PyCEGUI.Key.End)
		self.addKey("PAGE_UP", PyCEGUI.Key.PageUp)
		self.addKey("PAGE_DOWN", PyCEGUI.Key.PageDown)
		self.addKey("INSERT", PyCEGUI.Key.Insert)
		self.addKey("DELETE", PyCEGUI.Key.Delete)

		return
		# look for keys that could still be mapped; gotta map 'em all!
		print("* Unmapped FIFE keys:")
		for str_key in dir(fife.Key):
			try:
				int_key = fife.Key.__dict__[str_key]
			except KeyError:
				continue
			if not isinstance(int_key, int):
				continue
			if str_key not in self.keymap:
				print(str_key, int_key)
		print("* Unmapped CEGUI keys:")
		for str_key in dir(PyCEGUI.Key):
			try:
				int_key = PyCEGUI.Key.__dict__[str_key]
			except KeyError:
				continue
			if not isinstance(int_key, int):
				continue
			if int_key not in self.r_keymap:
				print(str_key, int_key)
		print("* End of unmapped keys")
