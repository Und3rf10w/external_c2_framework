import re
from helpers import common_utils

class SkeletonHandler(object):
	def __init__(self, target_skeleton):
		self.new_value = "" #given as `r'\\.\sample\unescaped\string'` (sans grave accents, include quotes) if str; if a number, just give the number
		self.target_skeleton = target_skeleton
		self.file_contents = ""
		self.regex_replacement_marker = '```\[var:::(\w*)\]```'
		self.target_var = "" # given as a normal string
		self.regex_replacement_value_marker = '```\[var:::'+self.target_var+'\]```' 

	def LoadSkeleton(self):
		try:
			skeleton_pointer = open(self.target_skeleton)
			self.file_contents = skeleton_pointer.read()
			skeleton_pointer.close()
		except Exception as e:
			print (common_utils.color(("Error loading skeleton %s: " %(str(self.target_skeleton))), warning=True, status=False) + "%s") % (str(e))
			# Prevent future issues from arising by clearing out the target_skeleton and file_content variables
			self.target_skeleton = ""
			self.file_contents = ""
			pass
	
	def ReplaceString(self, raw=False):
		replace_string = list(set(re.findall(self.regex_replacement_marker, self.file_contents)))
		for var in replace_string:
			if isinstance(self.new_value, (int, long, float, complex)) or raw == True:
				self.file_contents = re.sub(self.regex_replacement_value_marker.replace(str(self.new_value), self.target_var), str(self.new_value), self.file_contents)
			elif '"' in self.new_value :
				self.file_contents = re.sub(self.regex_replacement_value_marker.replace(self.new_value, self.target_var), repr(self.new_value).strip("'"), self.file_contents)
			else:
				self.file_contents = re.sub(self.regex_replacement_value_marker.replace(self.new_value, self.target_var), repr(self.new_value), self.file_contents)
	
	def GetCurrentFile(self):
		return self.file_contents
