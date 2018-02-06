import os
import skeleton
import skeleton.skeleton_handler
from helpers import common_utils

class Builder(object):
	def __init__(self):
			self.encoder = ""
			self.transport = ""
			self.framework = ""
			self.build_path = ""
			self.encoder_code = ""
			self.transport_code = ""

	def prep_builder(self):
		return ""

	def build_client_file(self, file_contents, output_path):
		try:
			output_pointer = open(output_path, 'wb+')
			output_pointer.write(file_contents)
			output_pointer.close()
			print(common_utils.color("Generated output file: ", status=True) + "%s") %(common_utils.color(str(output_path), status=False, yellow=True))
		except Exception as e:
			print (common_utils.color(("Error generating output file %s: " %(str(output_path))), warning=True, status=False) + "%s") % (str(e))
			pass

