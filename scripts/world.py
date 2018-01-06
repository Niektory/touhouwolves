# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

from fife import fife


class World(object):
	def __init__(self, application):
		self.application = application

	def pump(self, frame_time):
		pass
