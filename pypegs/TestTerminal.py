# pyPEGS
#
# Copyright (c) 2015, Arvid Rudling
# All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import bitstring


class TestTerminal(object):
	"""Drop-in replacement for Serial device, printing writes and returning pre-set data (using testPrepare(...) on read"""
	prepared_data = None
	open = False

	def __init__(self):
		self.open = True

	def write(self, data):
		assert self.open == True
		bytestream = bitstring.Bits(bytes=data, length=len(data) * 8)
		print "%s\t%s" % (bytestream.hex, bytestream.tobytes())

	def read(self):
		assert self.open == True
		assert self.prepared_data is not None, "TestTerminal error: read without prepared data"
		data = self.prepared_data
		self.prepared_data = None
		return data

	def setRTS(self, level):
		print "TestTerminal set RTS=%r" % level

	def setDTR(self, level):
		print "TestTerminal set DTS=%r" % level

	def close(self):
		self.open = False
		print "TestTerminal closed"

	def inWaiting(self):
		if self.prepared_data is not None:
			return len(self.prepared_data)
		else:
			return 0

	@staticmethod
	def testPrepare(device, data):
		if type(device) is TestTerminal:
			device.prepared_data = data
