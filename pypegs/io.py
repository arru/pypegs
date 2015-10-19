import time
import bitstring
import serial

### Animation constants

# references to left and right are from a viewer's perspective,
# looking at the face of the PEGS wearer
NOSE_GAP = 3
DISPLAY_EYE_WIDTH = 12
DISPLAY_HEIGHT = 7
FRAME_WIDTH = NOSE_GAP + DISPLAY_EYE_WIDTH * 2
FRAMERATE_MAX = 40
FRAMERATE_MIN = 1

### Memory & upload constants

PEGS_BAUDRATE = 57600
NUM_BANKS = 8
WELCOME_REFERENCE = "V1.0 - Caleb Pinckney"
FRAMES_MAGIC_SENTENCE = "0123456789012345678"

class Pegs(object):
	dev = None
	bank = None
	write_enabled = False

	def __init__(self, terminal):
		assert (terminal is not None)
		self.dev = terminal

	def _open_bank(self, bank):
		# can only do this once in a session, I think
		assert self.bank is None
		assert bank is not None
		assert bank >= 0
		assert bank < NUM_BANKS

		print "Opening bank %d for write" % bank

		TestTerminal.testPrepare(self.dev, "Bank Selected\x0d\x0a>")
		bank_select = SerialExchange(self.dev, "bank" + str(bank), "Bank Selected\x0d\x0a>")
		assert bank_select.execute()
		self.bank = bank

		TestTerminal.testPrepare(self.dev, "Writting Enabled\x0d\x0a>")
		enable_write = SerialExchange(self.dev, "enwrite", "Writting Enabled\x0d\x0a>")
		assert enable_write.execute()
		self.write_enabled = True

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
		line_bits.pos = line_bits.pos + NOSE_GAP
		composite_bits = composite_bits + line_bits.read('bits:4')
		bytes[1] = composite_bits.bytes

		bytes[2] = line_bits.read('bytes:1')

		return bytes

	def _upload_line(self, line):
		bytes = Pegs._pack_line(line)
		for b in bytes:
			self.dev.write(b)

	def upload_sequence(self, bank, framerate, data):
		"""Framerate argument shall be frames/sec. TODO: Convert as necessary"""

		assert len(data) >= 1
		assert framerate >= FRAMERATE_MIN
		assert framerate < FRAMERATE_MAX

		self._open_bank(bank)

		assert self.write_enabled == True
		assert self.bank is not None

		TestTerminal.testPrepare(self.dev, "Erased 4K\x0d\x0a>")
		erase = SerialExchange(self.dev, "Erase4K", "Erased 4K\x0d\x0a>")
		assert erase.execute()

		TestTerminal.testPrepare(self.dev, "Begin writting\x0d\x0a")
		write_long = SerialExchange(self.dev, "WriteLong", "Begin writting\x0d\x0a")
		assert write_long.execute()

		self.dev.write(FRAMES_MAGIC_SENTENCE)

		num_frames_byte = bitstring.Bits(uint=len(data), length=8)
		framerate_byte = bitstring.Bits(uint=framerate, length=8)
		meta_bytes = num_frames_byte + framerate_byte

		self.dev.write(meta_bytes.bytes)

		print "Uploading %d frames" % len(data)
		for frame in data:
			for line in frame:
				self._upload_line(line)
			print "*",

		print "Upload done"

	@staticmethod
	def connect_first():
		print "Opening serial port..."

		term = serial.Serial("/dev/tty.usbserial-A7041TBD", baudrate=PEGS_BAUDRATE)  # , timeout=5)

		print "Handshaking"

		TestTerminal.testPrepare(term, WELCOME_REFERENCE)
		handshake = SerialExchange(term, None, WELCOME_REFERENCE)
		if handshake.wait():
			print "These are PEGS"
			return Pegs(term)
		else:
			print "These are not PEGS"

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
			time.sleep(0.2)

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

	def write(self, data):
		bytestream = bitstring.Bits(bytes=data, length=len(data) * 8)
		print "%s\t%s" % (bytestream.hex, bytestream.tobytes())

	def read(self):
		assert self.prepared_data is not None, "TestTerminal error: read without prepared data"
		data = self.prepared_data
		self.prepared_data = None
		return data

	def inWaiting(self):
		if self.prepared_data is not None:
			return len(self.prepared_data)
		else:
			return 0

	@staticmethod
	def testPrepare(device, data):
		if type(device) is TestTerminal:
			device.prepared_data = data
