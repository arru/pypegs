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

			pixels = list(gif_frame.getdata())
			pixels = [pixels[i * input_width:(i + 1) * input_width] for i in xrange(frame_height)]

			for row in pixels:
				line_data = []
				for pix in row:
					# TODO: assumes 2-color palette where black (off) is first color
					# use color table instead
					assert pix == 0 or pix == 1
					line_data.append(pix)

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
