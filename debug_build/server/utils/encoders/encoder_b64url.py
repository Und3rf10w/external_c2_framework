import base64
import urllib

def encode(data):
	data = base64.b64encode(data)
	return urllib.quote_plus(data)[::-1]

def decode(data):
	data = urllib.unquote(data[::-1])
	return base64.b64decode(data)
