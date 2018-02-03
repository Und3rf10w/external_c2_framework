# A simple encoder module for Und3rf10w's implementation of the external_c2 spec for Cobalt Strike that simples base64 encodes/decodes .
import base64

def encode(data):
	return base64.b64encode(data)

def decode(data):
	return base64.b64decode(data)
