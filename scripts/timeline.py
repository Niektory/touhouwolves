# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife


class Timer:
	def __init__(self, name="", time=0, action=None, tick_action=None, del_on_clear=True):
		self.name = name
		self.time = time
		self.action = action
		self.tick_action = tick_action
		self.del_on_clear = del_on_clear

	def tick(self, time=1):
		if self.tick_action:
			self.tick_action()
		self.time -= time

	#def getTicks(self):
	#	return self.time


class RealTimeline(fife.TimeEvent):
	def __init__(self):
		super(RealTimeline, self).__init__(0)
		self.timers = []
		self.clock = 0
		self.multiplier = 1
		self.last_frame_time = 0

	def tick(self, time):
		self.last_frame_time = time
		self.clock += time
		for timer in self.timers:
			timer.tick(time)

	def addTimer(self, timer):
		self.timers.append(timer)

	def updateEvent(self, time):
		"""Called by FIFE. time = miliseconds since last update."""
		for timer in reversed(self.timers[:]):
			if timer.time <= 0:
				action = timer.action
				try:
					self.timers.remove(timer)
				except ValueError:
					print("Failed to remove timer!", timer.name)
					print(self.timers)
				else:
					if timer.action:
						action()
		# min prevents large jumps in time during loading etc.
		self.tick(min(time, 50) * self.multiplier)

	def list(self):
		for timer in self.timers:
			print(timer.name)

	def clear(self):
		for timer in self.timers[:]:
			if timer.del_on_clear:
				self.timers.remove(timer)


class GameTimeline(fife.TimeEvent):
	"""In-game clock."""
	def __init__(self, init_time, application):
		super(GameTimeline, self).__init__(0)
		self.application = application
		self.time = init_time
		#self.multiplier = 3600	# in-game clock speed; 1 = real time
		self.paused = False

	def updateEvent(self, time):
		"""Called by FIFE. time = miliseconds since last update."""
		if not self.paused:
			# min prevents large jumps in time during loading etc.
			self.time += self.application.settings.get("gameplay", "TimeAcceleration", 1) \
						* min(time, 50)
