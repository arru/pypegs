#!/usr/bin/env python

# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import os

from pypegs import Pegs
from pypegs.TestTerminal import TestTerminal
from pypegs.GifFile import GifFile
from pypegs.TextFile import TextFile

parser = argparse.ArgumentParser(description='Upload animations to PEGS party shades')
parser.add_argument('-p', '--port', help='Use the serial port PORT instead of auto-connect')
parser.add_argument('-f', '--framerate', type=int, metavar='FPS', default=None,
					help="Framerate in frames per second. Overrides any value present in input file.")
parser.add_argument('--invert', action="store_true", help='Swap light/dark in animation')
parser.add_argument("slot", type=int, help="Animation slot (1-%d) to upload to" % Pegs.NUM_BANKS)
parser.add_argument('file', help='Input file (24x7 or 30x7 .gif, or glasses designer .txt)')
parser.add_argument('--test', action="store_true",
					help='Run entire program through a dummy terminal instead of hardware PEGS')


args = parser.parse_args()

if args.test:
	shades = Pegs.Pegs(TestTerminal())
else:
	shades = Pegs.Pegs.connect(args.port)

if shades is None:
	exit()

filename, file_extension = os.path.splitext(args.file)

if file_extension.lower() == '.txt':
	anim_file = TextFile(args.file)
elif file_extension.lower() == '.gif':
	anim_file = GifFile(args.file)
else:
	print "Unsupported file extension: %s" % file_extension
	exit()

anim_file.read()

if args.invert == True:
	anim_file.invert()

shades.upload_sequence(args.slot - 1, anim_file.fps, anim_file.frames)
