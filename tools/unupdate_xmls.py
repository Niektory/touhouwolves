#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2018 Tomasz "Niektóry" Turowski

# converts FIFE object files back to the old format by removing the <assets> root element
# takes file names as arguments; for mass conversion use:
# find objects -name "*.xml" -exec python ./tools/unupdate_xmls.py {} +

from __future__ import print_function

from os.path import isfile
import sys
import xml.etree.ElementTree as ET

from xmlhelper import indent

files = [ f for f in sys.argv[1:] if isfile(f)]
for file in files:
	print("Parsing file:", file)
	try:
		tree = ET.parse(file)
	except ET.ParseError as e:
		print(e)
		continue
	root = tree.getroot()
	if root.tag == "object":
		print("Error: File is already in the old format.")
		continue
	if root.tag != "assets":
		print("Error: Not a valid fife object file.")
		continue
	for element in root:
		if element.tag == "object":
			new_root = element
			tree._setroot(new_root)
			indent(new_root)
			tree.write(file, encoding="UTF-8", xml_declaration=True)
			print("File converted successfully.")
			break
