# A transport module for Und3rf10w's implementation of the external_c2 spec of cobalt strike that utilizes a simple raw TCP socket as a covert channel.
# Not exactly covert...

import socket
import sys
import struct

# GHETTO CONFIG, should be read in from a master configuration file...
HOST = '0.0.0.0'
PORT = 8081

def prepTransport():
	"""
	This functions prepares the transport module for use
	"""
	# Create a socket
	global transSock
	global connSock
	transSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		print "Attempting to bind to " + str(HOST) + ":" + str(PORT)
		transSock.bind((HOST,PORT))
	except Exception as e:
		print "ERROR: %s" % (e)
		
	# Start listening
	transSock.listen(1)
	print "Socket now listening, waiting for connection from client..."

	# Wait to accept a connection from the client:
	connSock, addr = transSock.accept()
	# 'conn' socket object is the connection to the client, send data through that
	print 'Connected with client @ ' + addr[0] + ":" + str(addr[1])

	return connSock

def sendData(data):
	"""
	This function sends 'data' via the covert channel 'connSock'
	"""

	slen = struct.pack('<I', len(data))
	#connSock.sendall(slen + data)
	connSock.sendall(slen)
	connSock.sendall(data)

	return 0

def retrieveData():
	"""
	This function retrieves 'data' via the covert channel 'connSock' and returns it
	"""

	# My terribad first attempt at this based off of outflank example
	# I honestly have no idea what I was doing, but leaving it here just in case
	########
	# try:
	# 	data = transSock.recv(4)
	# except:
	# 	return("")
	# if len(data) < 4:
	# 	return()
	# slen = struct.unpack('<I', data)[0]
	# data = transSock.recv(slen)
	# while len(data) < slen:
	# 	data = data + transSock.recv(slen - len(data))
	# return(data)
	########

	# Realizing that I have to unpack the buffer length first:

	frameSize = ""
	while len(frameSize) != 4:
		frameSize = connSock.recv(4)

	dataSize = struct.unpack('<I', frameSize)[0]
	data = connSock.recv(dataSize)

	return data
