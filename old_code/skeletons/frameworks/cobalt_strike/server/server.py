import sys
import argparse
from utils import commonUtils
import configureStage
import establishedSession
import config
from time import sleep

def importModule(modName, modType):
	"""
	Imports a passed module as either an 'encoder' or a 'transport'; called with either encoder.X() or transport.X()
	"""
	prep_global = "global " + modType
	exec(prep_global)
	importName = "import utils." + modType + "s." + modName + " as " + modType
	exec(importName, globals())


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


	try:
		# Start with logic to setup the connection to the external_c2 server
		sock = commonUtils.createSocket()

		# TODO: Add logic that will check and recieve a confirmation from the client that it is ready to recieve and inject the stager
		# Poll covert channel for 'READY2INJECT' message from client
		#       * We can make the client send out 'READY2INJECT' msg from client periodically when it doesn't have a running beacon so that we don't miss it
		# if args.verbose:
		#       print commonUtils.color("Client ready to recieve stager")

		# #####################

		# Prep the transport module
		prep_trans = transport.prepTransport()

		# Let's get the stager from the c2 server
		stager_status = configureStage.loadStager(sock)

		if stager_status != 0:
			# Something went horribly wrong
			print commonUtils.color("Something went terribly wrong while configuring the stager!", status=False, warning=True)
			sys.exit(1)

		# TODO: Add logic that will check and recieve confirmation from the client that it is ready to recieve and process commands
		# Poll covert channel for 'READY4CMDS' message from client

		# Now that the stager is configured, lets start our main loop
		while True:
			if config.verbose:
				print commonUtils.color("Checking the c2 server for new tasks...")

			newTask = establishedSession.checkForTasks(sock)

			# once we have a new task (even an empty one), lets relay that to our client
			if config.debug:
				print commonUtils.color("Encoding and relaying task to client", status=False, yellow=True)
			establishedSession.relayTask(newTask)
			# Attempt to retrieve a response from the client
			if config.verbose:
				print commonUtils.color("Checking the client for a response...")
			b_response = establishedSession.checkForResponse()

			# Let's relay this response to the c2 server
			establishedSession.relayResponse(sock, b_response)
			sleep(config.C2_BLOCK_TIME/100) # python sleep is in seconds, C2_BLOCK_TIME in milliseconds


			# Restart this loop
	except KeyboardInterrupt:
		if config.debug:
			print commonUtils.color("\nClosing the socket to the c2 server")
		commonUtils.killSocket(sock)
		print commonUtils.color("\nExiting...", warning=True)
		sys.exit(0)

main()
