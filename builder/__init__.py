import os
import skeleton
import skeleton.skeleton_handler

class Builder(object):
	def __init__(self):
			self.encoder = ""
			self.transport = ""
			self.framework = ""
			self.build_path = ""

	def prep_builder(self):
		return ""

	def load_skeletons(self, skeletons):
		skeleton = []
		for filename in os.listdir(skeletons):
			skeleton.append(filename) 
		return skeleton

		# return completed_skeleton

	def build_client_file(self, file_contents, file_name):
		try:
			output_pointer = open("builds/%s") %(self.target_skeleton)
			output_pointer.write(self.file_contents)
			output_pointer.close()
			print(common_utils.color("Generated output file: ", status=True), + "%s") %(common_utils.color(str(output_pointer.name), status=False, yellow=True))
		except Exception as e:
			print (common_utils.color(("Error generating output file %s: " %(str(self.target_skeleton))), warning=True, status=False) + "%s") % (str(e))
			pass

