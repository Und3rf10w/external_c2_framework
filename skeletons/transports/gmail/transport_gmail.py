import email
import imaplib
from smtplib import SMTP
from smtplib import SMTP_SSL
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from time import sleep

# START OF GHETTO CONFIG SECTION
GMAIL_USER = ```[var:::gmail_user]```
GMAIL_PWD = ```[var:::gmail_pwd]```
SERVER = ```[var:::smtp_server]```
SERVER_PORT = int(```[var:::smtp_port]```)
RETRY_TIMER = int(```[var:::retry_time]```)
# END OF GHETTO CONFIG SECTION

def prepTransport():
	return 0

def send_server_notification(notification_data_frame):
	msg = MIMEMultipart()
	msg['From'] = GMAIL_USER
	msg['To'] = GMAIL_USER
	msg['Subject'] = "SessInit"
	message_content = str(notification_data_frame)

	msg.attach(MIMEText(str(message_content)))

	while True:
		try:
			# mailServer = SMTP(SERVER, SERVER_PORT)
			mailServer = SMTP_SSL(SERVER, SERVER_PORT)
			# mailServer.connect(SERVER, SERVER_PORT)
			# mailServer.ehlo()
			# mailServer.starttls()
			# mailServer.usetls()
			print "started tls"
			print mailServer.login(GMAIL_USER, GMAIL_PWD)
			print "logged in"
			mailServer.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
			print "sent " + str(len(msg.as_string())) + " bytes"
			mailServer.quit()
			break
		except Exception as e:
			print e
			sleep(RETRY_TIMER)  # wait RETRY_TIME seconds to try again

def sendData(beacon_id, data):
	msg = MIMEMultipart()
	msg['From'] = GMAIL_USER
	msg['To'] = GMAIL_USER
	msg['Subject'] = str(beacon_id) + ":New4You"
	message_content = str(data)
	print "got msg_content"

	msg.attach(MIMEText(str(message_content)))

	while True:
		try:
			#mailServer = SMTP(SERVER, SERVER_PORT)
			mailServer = SMTP_SSL(SERVER, SERVER_PORT)
			#mailServer.connect(SERVER, SERVER_PORT)
			#mailServer.ehlo()
			#mailServer.starttls()
			#mailServer.usetls()
			print "started tls"
			print mailServer.login(GMAIL_USER,GMAIL_PWD)
			print "logged in"
			mailServer.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
			print "sent " + str(len(msg.as_string())) + " bytes"
			mailServer.quit()
			break
		except Exception as e:
			print e
			sleep(RETRY_TIMER) # wait RETRY_TIME seconds to try again


def check_for_new_clients():
	c = imaplib.IMAP4_SSL(SERVER)
	c.login(GMAIL_USER, GMAIL_PWD)
	c.select("INBOX")

	typ, id_list = c.search(None, '(UNSEEN SUBJECT "SessInit")')
	print id_list[0].split()
	if not id_list[0].split():
		return None
	else:
		for msg_id in id_list[0].split():
			msg = c.fetch(msg_id, '(RFC822)')
			msg = ([x[0] for x in msg][1])[1]
			for part in email.message_from_string(msg).walk():
				msg = part.get_payload()
				c.logout()
			return msg

def retrieveData(beacon_id):
	c= imaplib.IMAP4_SSL(SERVER)
	c.login(GMAIL_USER, GMAIL_PWD)
	c.select("INBOX")

	#typ, id_list = c.uid('search', None, "(UNSEEN SUBJECT 'New4You')".format(uniqueid))
	while True:
		typ, id_list = c.search(None, '(UNSEEN SUBJECT "' + str(beacon_id) + ':Resp4You")')
		print id_list[0].split()
		if not id_list[0].split():
			sleep(RETRY_TIMER) # wait for RETRY_TIME seconds before checking again
			c.select("INBOX")
			typ, id_list = c.search(None, '(UNSEEN SUBJECT "' + str(beacon_id) + ':Resp4You")')
			pass
		else:
			for msg_id in id_list[0].split():
				msg = c.fetch(msg_id, '(RFC822)')
				#c.store(msg_id, '+FLAGS', '\SEEN')
				msg = ([x[0] for x in msg][1])[1]
				for part in email.message_from_string(msg).walk():
					msg = part.get_payload()
				c.logout()
				return msg
