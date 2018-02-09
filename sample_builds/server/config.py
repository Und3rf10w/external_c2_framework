# TODO: Have a proper function that reads in a config

# DEBUG: <START GHETTO CONFIG>
############################################
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

ENCODER_MODULE = "encoder_b64url"
TRANSPORT_MODULE = "transport_gmail"

###########################################
# DEBUG: </END GHETTO CONFIG>

# Anything taken in from argparse that you want to make avaialable goes here:
verbose = False
debug = False