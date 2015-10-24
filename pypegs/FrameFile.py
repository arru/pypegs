# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import Pegs


class FrameFile(object):
	"""Base class for animation files loaded into PEGS"""
	path = None
	_file = None

	fps = None
	frames = None

	def __init__(self, path):
		self.path = path
		assert self.path is not None

	def invert(self):
		inverted_frames = []
		assert self.frames is not None

		for frame in self.frames:
			new_frame = []
			assert len(frame) == Pegs.DISPLAY_HEIGHT
			for line in frame:
				new_line = []
				assert len(line) == Pegs.FRAME_WIDTH

				for pixel in line:
					if pixel == 1:
						pixel_inv = 0
					else:
						assert pixel == 0
						pixel_inv = 1

					new_line.append(pixel_inv)

				new_frame.append(new_line)

			inverted_frames.append(new_frame)

		self.frames = inverted_frames
