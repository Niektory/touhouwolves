#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

# copy this file (and scripts/xmlhelper.py) to a directory with images
# and run it there to generate default object XML files tor them
# doesn't overwrite existing XML files

from __future__ import print_function

from os import listdir
from os.path import isfile, splitext
import xml.etree.ElementTree as ET

from xmlhelper import indent

files = [ f for f in listdir('.') if isfile(f) ]
for file in files:
	if splitext(file)[1].lower() not in ('.png', '.jpg', '.jpeg'):
		continue
	if isfile(splitext(file)[0] + '.xml'):
		continue
	print('generating xml for image:', file)
	root = ET.Element("assets")
	tree = ET.ElementTree(element=root)
	object_element = ET.Element("object")
	object_element.set("id", splitext(file)[0])
	object_element.set("namespace", "steamfolktales")
	object_element.set("blocking", "0")
	object_element.set("static", "1")
	root.append(object_element)
	image_element = ET.Element("image")
	image_element.set("source", file)
	image_element.set("direction", "0")
	image_element.set("x_offset", "0")
	image_element.set("y_offset", "0")
	object_element.append(image_element)
	indent(root)
	tree.write(splitext(file)[0] + '.xml', encoding="UTF-8", xml_declaration=True)
