# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class FrameFile(object):
	"""Base class for animation files loaded into PEGS"""
	path = None
	_file = None

	fps = None
	frames = None

	def __init__(self, path):
		self.path = path
		assert self.path is not None
