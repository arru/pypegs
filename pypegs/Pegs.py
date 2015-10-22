import time
import glob
import os

import bitstring
import serial


### Animation constants

# references to left and right are from a viewer's perspective,
# looking at the face of the PEGS wearer
DISPLAY_EYE_WIDTH = 12
DISPLAY_HEIGHT = 7
NOSE_GAP = 6.1832
PIXEL_ASPECT = 0.63007
FRAME_WIDTH = DISPLAY_EYE_WIDTH * 2
FRAMERATE_MAX = 60
FRAMERATE_MIN = 1

### Memory & upload constants

SERIAL_DEV_ROOT = "/dev/"
PEGS_BAUDRATE = 57600
# Time delay in seconds between transmitted pixel bytes, based on measured output
# from PEGS glasses designer. Disable = set to 0.0
UPLOAD_THROTTLE = 0.000984
NUM_BANKS = 8
MAX_FRAMES = 160
WELCOME_REFERENCE = "V1.0 - Caleb Pinckney"
FRAMES_MAGIC_SENTENCE = "0123456789012345678"


class Pegs(object):
	dev = None
	bank = None
	write_enabled = False

	def __init__(self, terminal):
		assert (terminal is not None)
		self.dev = terminal

	def _close(self):
		self.dev.close()

		assert self.write_enabled == True
		self.write_enabled = False
		self.bank = None
		
		print "PEGS connection closed. Please disconnect PEGS."

	def _open_bank(self, bank):
		# can only do this once in a session, I think
		assert self.bank is None
		assert bank is not None
		assert bank >= 0
		assert bank < NUM_BANKS

		print "Opening PEGS for flash write operation"
		TestTerminal.testPrepare(self.dev, "Bank Selected\x0d\x0a>")
		bank_select = SerialExchange(self.dev, "bank" + str(bank), "Bank Selected\x0d\x0a>")
		assert bank_select.execute()
		self.bank = bank

		TestTerminal.testPrepare(self.dev, "Writting Enabled\x0d\x0a>")
		enable_write = SerialExchange(self.dev, "enwrite", "Writting Enabled\x0d\x0a>")
		assert enable_write.execute()

		self.write_enabled = True
		print "Bank %d opened for write. DO NOT DISCONNECT PEGS." % self.bank

	@staticmethod
	def _pack_line(line):
		# for some reason, line bits are stored left-to-right but transmitted
		# right-to-left (omitting the "nose gap" pixels 13-15)
		line_string = "0b"
		for b in reversed(line):
			line_string = line_string + str(b)

		line_bits = bitstring.ConstBitStream(line_string)

		bytes = [None, None, None]
		bytes[0] = line_bits.read('bytes:1')

		composite_bits = line_bits.read('bits:4')
		composite_bits = composite_bits + line_bits.read('bits:4')
		bytes[1] = composite_bits.bytes

		bytes[2] = line_bits.read('bytes:1')

		return bytes

	def upload_sequence(self, bank, framerate, frames):
		"""Framerate argument shall be frames/sec. TODO: Convert as necessary"""

		num_frames = len(frames)
		assert num_frames >= 1
		assert num_frames <= MAX_FRAMES
		assert framerate >= FRAMERATE_MIN
		assert framerate <= FRAMERATE_MAX

		# Prepare frames
		pixel_stream = []
		for frame in frames:
			assert len(frame) == DISPLAY_HEIGHT
			for line in frame:
				assert len(line) == FRAME_WIDTH
				line_bytes = Pegs._pack_line(line)
				assert len(line_bytes) == 3
				pixel_stream.extend(line_bytes)

		assert len(pixel_stream) == ((num_frames * DISPLAY_HEIGHT * DISPLAY_EYE_WIDTH * 2) / 8)
		for b in pixel_stream:
			assert b is not None

		num_frames_byte = bitstring.Bits(uint=num_frames, length=8)
		framerate_byte = bitstring.Bits(uint=framerate, length=8)
		meta_bytes = num_frames_byte + framerate_byte

		# Open PEGS for write
		self._open_bank(bank)

		assert self.write_enabled == True
		assert self.bank is not None

		print "Erasing"
		TestTerminal.testPrepare(self.dev, "Erased 4K\x0d\x0a>")
		erase = SerialExchange(self.dev, "Erase4K", "Erased 4K\x0d\x0a>")
		assert erase.execute()

		TestTerminal.testPrepare(self.dev, "Begin writting\x0d\x0a")
		write_long = SerialExchange(self.dev, "WriteLong", "Begin writting\x0d\x0a")
		assert write_long.execute()

		print "Uploading %d frames" % num_frames

		# Write header
		self.dev.write(FRAMES_MAGIC_SENTENCE)

		self.dev.write(meta_bytes.bytes)

		# Write frame frames
		chunk_counter = 0
		last_tx = 0

		for chunk in pixel_stream:
			while time.clock() < last_tx + UPLOAD_THROTTLE:
				time.sleep(UPLOAD_THROTTLE / 5)

			last_tx = time.clock()
			self.dev.write(chunk)

			chunk_counter = chunk_counter + 1
			if chunk_counter % ((DISPLAY_HEIGHT * DISPLAY_EYE_WIDTH * 2) / 8) == 0:
				print "*",

		print
		print "Upload done"

		self._close()

	@staticmethod
	def connect(port_path=None):
		print "Opening serial port..."

		# This way of auto-finding PEGS serial port only works on POSIX systems

		if port_path is None:
			os.chdir(SERIAL_DEV_ROOT)
			ports = glob.glob("tty.usbserial*")
			if len(ports) == 1:
				port_path = ports[0]
			else:
				if len(ports) > 1:
					print "Found more than one serial unit that could be PEGS. Please choose the one to connect to and re-run this command with this port specified in the arguments."
					for p in ports:
						print p
				else:
					print "Could not find PEGS. Make sure they are connected, turned on, and you're either running Mac OSX 10.9 or later, or installed the FTDI drivers (see readme.md)"
				return None

		term = serial.Serial(port_path, baudrate=PEGS_BAUDRATE)  # , timeout=5)

		print "Handshaking"

		TestTerminal.testPrepare(term, WELCOME_REFERENCE)
		handshake = SerialExchange(term, None, WELCOME_REFERENCE)
		if handshake.wait():
			print "Connected to PEGS on port %s" % port_path
			return Pegs(term)
		else:
			print "Device port %s is not PEGS (or handshake failed for some other reason)" % port_path

		return None


class SerialExchange:
	TIMEOUT = 10.00

	def __init__(self, terminal, message, ackn=None):
		self.term = terminal
		self.message = message

		if ackn is None:
			self.acknowledge = message
		else:
			self.acknowledge = ackn

		assert self.term is not None

	def wait(self):
		wait_start = time.time()
		indata = ""

		# wait for response to begin
		while self.term.inWaiting() == 0 and time.time() - wait_start < self.TIMEOUT:
			time.sleep(self.TIMEOUT / 100)

		# listen for response until message found (or timeout)
		while time.time() - wait_start < self.TIMEOUT:
			if self.term.inWaiting() > 0:
				indata = indata + self.term.read()
				if self.acknowledge in indata:
					return True

		print "Acknowledge not found in:\t'%s'" % indata
		return False

	def execute(self):
		self.term.write(self.message)
		return self.wait()


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
