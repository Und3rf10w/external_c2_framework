import PIL
from PIL import Image
import base64
import zlib

# <START OF GHETTO CONFIG>
VERSION = 0
# </END OF GHETTO CONFIG>


def encode(data):
	# Recieves raw data as input
	# Start with compressing it with zlib
	# Then base64 the output to make it nice ascii
	data = base64.b64encode(zlib.compress(data, 9))


	# TODO: add a feature where if len(data_list) > 255, the last image will have a new album URL
	# Regardless if len(data) > 1079, we'll still have it as a list
	data_list = [data[i:i+1079] for i in range(0, len(data), 1079)]


	print len(data_list) #DEBUG

	# We'll use the upperleftmost pixel as a pseudo header:
	# ($ENCODER_VERSION, $PHOTO_NUM_IN_SERIES, $TOTAL_NUM_OF_PHOTOS_IN_SERIES)

	image_list = []
	photo_id = 1
	# Loop through number of elements in the datalist
	for photo_id in range(0, len(data_list) - 1):
		data_to_write = data_list[photo_id]
		
		# Create a new image
		img = Image.new('RGB', (1920,1080), color = 'red')
		pix = img.load()
		# Loop through the number of bytes in data_to_write
		for byte in data_to_write:
			# Loop through diaganol pixels
			for x in range(1, img.size[1] + 1):
				# Write the byte to the blue value in the pixel
				pix[x,x] = (pix[x,x][0], pix[x,x][1], ord(byte))
				x = x + 1
				pass
			pass
		pix[0,0][0] = (VERSION, photo_id, len(data_list) - 1)
		image_list.append(img.load)
		pass

	# Now we have image_list with a list of stegoed PIL images that can be sent
	return image_list

def decode(data):
	# Recieves a list of images as input
	# Start with ordering list list of images

	# logic to order the images
	ordered_images = []
	for image in data:
		pix = Image.load(image)
		# DEBUG
		# pix[0,0][1] == order of photo in series
		print "Adding image " + str(pix[0,0][1]) + " of " + str(pix[0,0][2])
		image_id = pix[0,0][1]
		ordered_images.update({image_id: image})

	# Now lets order our list
	ordered_images = sorted(ordered_images)

	byte_list = []

	# Iterate through our ordered list of images
	# to rebuild our data
	for k in ordered_images.keys():
		image = ordered_image[k]
		pix = Image.load(image)
			for x in range(image.size[1] - 1):
				if x == 0:
					# Ignore topleft pixel
					x = x + 1
					pass
				# Add ord(byte) to bytelist
				byte_list.append(chr(pix[x,x][2]))
				pass

	# Now we have a list of bytes that are a base64 encoded string
	decoded_data = base64.b64decode(''.join(byte_list))

	# Return the decoded_data
	return decoded_data
