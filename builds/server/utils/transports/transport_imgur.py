from imgurpython import ImgurClient
import PIL
from PIL import Image
from cStringIO import StringIO
from time import sleep
from sys import exit
import urlparse

# YOU NEED TO GET A TOKEN FOR YOUR APPLICATION FIRST.=
# SET UP YOUR ACCOUNT.


# <START OF GHETTO CONFIG SECTION>
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


def sendTokens(tokens):
	# Sends tokens in plain text. Eventually, I'd like to get it so I can
	# just pass it to the encoder, but this works for a prototype
		
	img = Image.new('RGB', (1920,1080), color = 'red')
	pix = img.load()
	token_list = list(bytearray(tokens))
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
	print album_object #DEBUG

	# Upload our image to the album
	img_byte_array = StringIO()
	img.save(img_byte_array, format='JPEG')
	y = client.upload(image=img_byte_array.getvalue(), config=fields)
	print y #DEBUG

	# Return the token's album hash
	return album_object['deletehash']


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
	data = str(access_token + "," + refresh_token)
	token_album_hash = sendTokens(data)

	# Loop to check and see if our token album has been deleted
	#   if not, sleep 60 seconds and try again
	while True:
		try: 
			client.get_album(token_album_hash)
			sleep(60)
		# Couldn't find the album, need to set a general exception that tries again, but also need to find what kind
		# of exception we'll get when the album no longer exists
		

		# except AlbumNotFoundError:
		#	break

		except Exception as e:
			print "Caught unknown exception: %s" % (str(exception))


	# Client has recieved the tokens
	return 0


def sendData(data):
	# Transport will receiving a list of images
	# Application will have already encoded the data
	# Logic will probably be different for client,
	# indicating that we're going to run into issues
	

def retrieveData():

