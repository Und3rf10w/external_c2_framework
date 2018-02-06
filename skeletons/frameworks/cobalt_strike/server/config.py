# TODO: Have a proper function that reads in a config

# DEBUG: <START GHETTO CONFIG>
############################################
############################################
# Address of External c2 server
EXTERNAL_C2_ADDR = ```[var:::external_c2_addr]```

# Port of external c2 server
EXTERNAL_C2_PORT = ```[var:::external_c2_port]```

# The name of the pipe that the beacon should use
C2_PIPE_NAME = ```[var:::c2_pipe_name]```

# A time in milliseconds that indicates how long the External C2 server should block when no new tasks are available
C2_BLOCK_TIME = ```[var:::c2_block_time]```

# Desired Architecture of the Beacon
C2_ARCH = ```[var:::c2_arch]```

# How long to wait (in seconds) before polling the server for new tasks/responses
IDLE_TIME = ```[var:::c2_block_time]```

ENCODER_MODULE = ```[var:::encoder]```
TRANSPORT_MODULE = ```[var:::transport]```

###########################################
# DEBUG: </END GHETTO CONFIG>

# Anything taken in from argparse that you want to make avaialable goes here:
verbose = False
debug = False