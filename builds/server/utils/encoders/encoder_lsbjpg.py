import PIL
from PIL import Image
import base64
import zlib

# <START OF GHETTO CONFIG>
VERSION = 0
# </END OF GHETTO CONFIG>


def encode(data, **kwargs):
	photo_id = kwargs['photo_id']
	image_list = []
	img = Image.new('RGB', (1920,1080), color = 'red')
	pix = img.load()
	for byte in data:
		for x in range(1, img.size[1]):
			pix[x,x] = (pix[x,x][0], pix[x,x][1], ord(byte))
			x = x + 1
			pass
		pass
	pix[0,0] = (VERSION, photo_id, len(data_list) - 1)
	image_list.append(img.load)
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
