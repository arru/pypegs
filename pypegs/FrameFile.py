class FrameFile(object):
	"""Base class for animation files loaded into PEGS"""
	path = None
	_file = None

	fps = None
	frames = None

	def __init__(self, path):
		self.path = path
		assert self.path is not None
