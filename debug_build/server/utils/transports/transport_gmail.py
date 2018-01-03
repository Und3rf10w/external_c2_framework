import email
import imaplib
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from time import sleep

# START OF GHETTO CONFIG SECTION
GMAIL_USER = 'example@gmail.com'
GMAIL_PWD = 'hunter2'
SERVER = 'smtp.gmail.com'
SERVER_PORT = 587
# END OF GHETTO CONFIG SECTION

def prepTransport():
	return 0

def sendData(data):
	msg = MimeMultipart()
	msg['From'] = GMAIL_USER
	msg['To'] = GMAIL_USER
	msg['Subject'] = "New4You!"
	message_content = data

	msg.attach(MIMEText(str(message_content)))

	while True:
		try:
			mailServer = SMTP()
			mailServer.connect(SERVER, SERVER_PORT)
			mailServer.starttls()
			mailServer.login(GMAIL_USER,GMAIL_PWD)
			mailServer.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
			mailServer.quit()
			break
		except Exception as e:
			sleep(10) # wait 10 seconds to try again


def retrieveData():
	c= imaplib.IMAP4_SSL(SERVER)
	c.login(GMAIL_USER, GMAIL_PWD)
	c.select("INBOX")

	typ, id_list = c.uid('search', None, "(UNSEEN SUBJECT 'New4You')".format(uniqueid))

	for msg_id in id_list[0].split():
		msg = c.uid('fetch', msg_id, '(RFC822)')
		return msg
	c.logout()

