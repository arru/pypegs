# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

import Pegs
from FrameFile import FrameFile


class TextFile(FrameFile):
	"""Reader for PEGS glasses designer .txt files"""
	TXT_FRAME_HEIGHT = 8
	TXT_NOSE_GAP = 3

	HEADER_RE = re.compile("6,(\d+),(\d+)")
	PIXELS_RE = re.compile("[01]{28}")

	@staticmethod
	def parseLine(line):
		line_data = []

		for c, char in enumerate(line):
			if c < Pegs.DISPLAY_EYE_WIDTH * 2 + TextFile.TXT_NOSE_GAP:
				assert (char == "0" or char == "1")
				if c < Pegs.DISPLAY_EYE_WIDTH or c >= Pegs.DISPLAY_EYE_WIDTH + TextFile.TXT_NOSE_GAP:
					line_data.append(int(char))

		assert len(line_data) == Pegs.FRAME_WIDTH
		return line_data

	def read(self):
		num_frames = None
		self._file = open(self.path)

		output_frames = []
		current_frame = []

		frame_line_counter = 0
		got_blank = False

		with self._file as f:
			for line in f:
				if num_frames is None:
					header = self.HEADER_RE.match(line)
					if header is not None:
						num_frames = int(header.group(1))
						self.fps = int(header.group(2))
				elif frame_line_counter > num_frames * Pegs.DISPLAY_HEIGHT:
					# All frames read, done
					break
				else:
					pixels = self.PIXELS_RE.match(line)

					if pixels is None:
						# expecting blank line, but only between frames
						assert len(current_frame) == 0
						got_blank = True
					else:
						assert got_blank
						assert num_frames is not None

						if len(current_frame) < Pegs.DISPLAY_HEIGHT:
							current_frame.append(self.parseLine(line))
							frame_line_counter = frame_line_counter + 1
						else:
							# One trash line in PEGS .txt files, skip it

							assert len(current_frame) == Pegs.DISPLAY_HEIGHT
							output_frames.append(current_frame)
							current_frame = []
							got_blank = False

		self._file.close()

		assert num_frames >= 1
		assert len(output_frames) == num_frames

		self.frames = output_frames
