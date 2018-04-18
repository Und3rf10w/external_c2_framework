import PIL
from PIL import Image
from cStringIO import StringIO
import base64
import zlib

# <START OF GHETTO CONFIG>
VERSION = 0
# </END OF GHETTO CONFIG>

def encode(data, photo_id=1, list_size=1):
	img = Image.new('RGB', (4320,4320), color = 'red')
	pix = img.load()
	x = 1
	for byte in data:
		pix[x,x] = (pix[x,x][0], pix[x,x][1], ord(byte))
		x = x + 1
		pass
	pix[0,0] = (VERSION, photo_id, list_size)
	img_byte_array = StringIO()
	img.save(img_byte_array, format='PNG')
	return img_byte_array

def decode(image):
	stego_pix = image.load()
	byte_list = []
	
	for y in range(1, image.size[1]):
		# Add our byte we wnat
		byte_list.append(chr(stego_pix[y,y][2]))
	pass

	return ''.join(byte_list)
