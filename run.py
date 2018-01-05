#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

#from traceback import print_exc

from scripts.error import LogException

if __name__ == '__main__':
	with LogException():
		from fife.extensions.pychan.fife_pychansettings import FifePychanSettings
		from scripts.application import Application
		settings = FifePychanSettings(
			app_name="touhouwolves",
			settings_file="./settings.xml",
			settings_gui_xml="")
		application = Application(settings)
		application.run()
