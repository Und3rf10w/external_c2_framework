from imgurpython import ImgurClient
import PIL
from PIL import Image
import io

# YOU NEED TO GET A TOKEN FOR YOUR APPLICATION FIRST.=
# SET UP YOUR ACCOUNT.

# <START OF GHETTO CONFIG SECTION>
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
		for x in range(img.size[1] - 1):			
			# Insert a UPDATE_TOKENS header
			if x == 0:
				pix[x,x] = (1, 1, 1)
				pass
			# Write the byte to the blue value in the pixel
			pix[x,x] = (pix[x,x][0], pix[x,x][1], byte)
			x += 1
			pass
		pass

	# Upload image to new album
	fields = {
		'title' = "TK4U"
		'privacy' = "public"
	}
	album_object = client.create_album(fields)
	print album_object #DEBUG

	# Upload our image to the album
	img_byte_array = io.BytesIO()
	tokenimg = img.save(img_byte_array, FORMAT='JPG')
	y = client.upload(image=img_byte_array.getvalue(), album=album_object['id'], name="tkns")
	# y = client.album_add_images(album_object['id'], img)
	print y #DEBUG

	# Return the token's album id
	return album_object['id']


def prepTransport():
    global client
    client = ImgurClient(client_id, client_secret)

    # Auth to imgur
    authorization_url = client.get_auth_url('token')

    print "Go to the following URL: {0}".format(authorization_url)

    try:
    	token = raw_input("Insert the provided token: ")
    except:
    	token = input("Insert the provided token: ")

    global credentials
    credentials = client.authorize(token, 'token')
    client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

    # Sending access and refresh token to client
    data = str(credentials['access_token'] + "," + credentials['refresh_token'])
    token_album_id = sendTokens(data)

    # Loop to check and see if our token album has been deleted
    #   if not, sleep 60 seconds and try again
    while True:


    return 0


def sendData(data):
	# Transport will receiving a list of images
	# Application will have already encoded the data
	# Logic will probably be different for client,
	# indicating that we're going to run into issues
	

def retrieveData():

