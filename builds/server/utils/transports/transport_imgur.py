from imgurpython import ImgurClient
import PIL
from PIL import Image
from cStringIO import StringIO
from time import sleep
from sys import exit
import urlparse
import base64
import requests

# YOU NEED TO GET A TOKEN FOR YOUR APPLICATION FIRST.=
# SET UP YOUR ACCOUNT.


# <START OF GHETTO CONFIG SECTION>
TOKEN_LEN = 81 # Don't change this
USERNAME = ''
client_id = ''
client_secret = ''
access_token = 
refresh_token = 
# </END OF GHETTO CONFIG SECTION>

# Server's transport will handle access tokens and whatnot.

# client's prepTransport will have to handle token refreshes. 
# TODO: Client won't last more than a month without this logic.
#   - need to add authtoken refresh logic

def prepClientTransport():
	global client
	client = ImgurClient(client_id, client_secret)

	getTokens()
	return 0

def deleteAlbums(albums):
	for album in albums:
		client.album_delete(album.id)
	return 0

def deleteImages(images):
	for imageid in images:
		client.delete_image(imageid)
	return 0

def getTokens():
	account_albums = client.get_account_albums(USERNAME)

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
	deleteAlbums(account_albums)
	client.delete_image(token_image.id)

	return 0

def sendTokens(tokens):
	# Sends tokens in plain text. Eventually, I'd like to get it so I can
	# just pass it to the encoder, but this works for a prototype
		
	img = Image.new('RGB', (1920,1080), color = 'red')
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
	y = client.make_request('POST', 'upload', image_upload_fields)


	# I know this is a very weird looking loop, but it was to fix a very weird bug
	while True:
		account_albums = client.get_account_albums(USERNAME)
		try:
			if account_albums[0].id:
				for album in account_albums:
					if album.id == album_object['id']:
						print "Album still exists, waiting 60 seconds for client to send new album"
						sleep(60)
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
	

def retrieveData():

