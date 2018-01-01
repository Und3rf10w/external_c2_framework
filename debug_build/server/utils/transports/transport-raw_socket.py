# A transport module for Und3rf10w's implementation of the external_c2 spec of cobalt strike that utilizes a simple raw TCP socket as a covert channel.
# Not exactly covert...
import socket
import sys

# GHETTO CONFIG, should be read in from a master configuration file...
HOST = '0.0.0.0'
PORT = 8081

def prepTransport():
	"""
	This functions prepares the transport module for use
	"""
	# Create a socket
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
	conn, addr = transSock.accept()
	print 'Connected with client @ ' + addr[0] + ":" + str(addr[1])

	return transSock

def sendData(transSock, data):
	"""
	This function sends 'data' via the covert channel 'transSock'
	"""

	slen = struct.pack('<I', len(data))
	transSock.sendall(slen + data)

	return 0

def retrieveData(transSock):
	"""
	This function retrieves 'data' via the covert channel 'transSock' and returns it
	"""

	try:
		data = transSock.recv(4)
	except:
		return("")
	if len(data) < 4:
		return()
	slen = struct.unpack('<I', data)[0]
	data = transSock.recv(slen)
	while len(data) < slen:
		data = data + transSock.recv(slen - len(data))
	return(data)	
