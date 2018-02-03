import email
import imaplib
from smtplib import SMTP
from smtplib import SMTP_SSL
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from time import sleep

# START OF GHETTO CONFIG SECTION
GMAIL_USER = 'example@gmail.com'
GMAIL_PWD = 'hunter2'
SERVER = 'smtp.gmail.com'
SERVER_PORT = 465
# END OF GHETTO CONFIG SECTION

def prepTransport():
	return 0

def sendData(data):
	msg = MIMEMultipart()
	msg['From'] = GMAIL_USER
	msg['To'] = GMAIL_USER
	msg['Subject'] = "New4You"
	message_content = data
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
			sleep(10) # wait 10 seconds to try again

def retrieveData():
	c= imaplib.IMAP4_SSL(SERVER)
	c.login(GMAIL_USER, GMAIL_PWD)
	c.select("INBOX")

	#typ, id_list = c.uid('search', None, "(UNSEEN SUBJECT 'New4You')".format(uniqueid))
	while True:
		typ, id_list = c.search(None, '(UNSEEN SUBJECT "Resp4You")')
		print id_list[0].split()
		if not id_list[0].split():
			sleep(10) # wait for 10 seconds before checking again
			c.select("INBOX")
			typ, id_list = c.search(None, '(UNSEEN SUBJECT "Resp4You")')
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

