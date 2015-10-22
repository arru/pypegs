# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PIL import Image

import Pegs
from FrameFile import FrameFile
import Image


class GifFile(FrameFile):
	THRESHOLD = 127

	def read(self):
		output_frames = []
		input_width = None

		self.file = open(str(self.path), 'rb')

		gif_frame = Image.open(self.file)
		self.fps = int(round(1000 / gif_frame.info['duration']))

		frame_counter = 0
		while gif_frame:
			current_frame = []

			frame_width, frame_height = gif_frame.size
			if input_width == None:
				input_width = frame_width
				assert input_width == Pegs.FRAME_WIDTH  # or frame_width == Pegs.FRAME_WIDTH + round(int(Pegs.NOSE_GAP))

			# Not sure whether GIF frames can vary in size, but better safe than sorry
			assert frame_width == input_width
			assert frame_height == Pegs.DISPLAY_HEIGHT

			pixels = list(gif_frame.convert('RGB').getdata())
			pixels = [pixels[i * input_width:(i + 1) * input_width] for i in xrange(frame_height)]

			for row in pixels:
				line_data = []
				for pix in row:
					if max(pix[0], pix[1], pix[2]) > GifFile.THRESHOLD:
						line_data.append(1)
					else:
						line_data.append(0)

				assert len(line_data) == Pegs.FRAME_WIDTH
				current_frame.append(line_data)

			assert len(current_frame) == Pegs.DISPLAY_HEIGHT
			output_frames.append(current_frame)
			frame_counter += 1
			try:
				gif_frame.seek(frame_counter)
			except EOFError:
				break;

		self.frames = output_frames

		self.file.close()
