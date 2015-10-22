#!/usr/bin/env python

import argparse
import os

from pypegs import Pegs
from pypegs.Pegs import TestTerminal
from pypegs.GifFile import GifFile
from pypegs.TextFile import TextFile

parser = argparse.ArgumentParser(description='Upload animations to PEGS party shades')
parser.add_argument('--test', action="store_true",
					help='Run entire program through a dummy terminal instead of hardware PEGS')
parser.add_argument('-p', '--port', help='Use this serial port PORT instead of auto-connect')
parser.add_argument('-f', '--framerate', type=int, metavar='FPS', default=None,
					help="Framerate in frames per second. Overrides any value present in input file.")
parser.add_argument("slot", type=int, help="Animation slot (1-%d) to upload to" % Pegs.NUM_BANKS)
parser.add_argument('file', help='Input file (.gif or .txt)')

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

shades.upload_sequence(args.slot - 1, anim_file.fps, anim_file.frames)
