import re

class SkeletonHandler(object):
	def __init__(self, target_skeleton, target_var, new_value):
		self.new_value = new_value #given as `r'\\.\sample\unescaped\string'` (sans grave accents, include quotes) if str; if a number, just give the number
		self.target_skeleton = target_skeleton
		self.file_contents = ""
		self.regex_replacement_marker = '```\[var:::(\w*)\]```'
		self.regex_replacement_value_marker = '```\[var:::'+self.new_value+'\]```' 
		self.target_var = target_var # given as a normal string

	def LoadSkeleton(self):
		try:
			skeleton_pointer = open(self.target_skeleton)
			self.file_contents = skeleton_pointer.read()
			skeleton_pointer.close()
		except Exception as e:
			print (commonUtils.color(("Error loading skeleton %s: " %(str(self.target_skeleton))), warning=True, status=False) + "%s") % (str(e))
			# Prevent future issues from arising by clearing out the target_skeleton and file_content variables
			self.target_skeleton = ""
			self.file_contents = ""
			pass
	
	def ReplaceString(self):
		replace_string = list(set(re.findall(self.regex_replacement_marker, self.file_contents)))
		for var in replace_string:
			if isinstance(self.new_value, (int, long, float, complex)):
				self.file_contents = re.sub(self.regex_replacement_value_marker.replace(str(self.new_value), self.target_var), str(self.new_value), self.file_contents)
			else:
				self.file_contents = re.sub(self.regex_replacement_value_marker.replace(str(self.new_value), self.target_var), repr(str(self.new_value)), self.file_contents)
	
	def GetCurrentFile(self):
		return self.file_contents

	# def WriteGeneratedFile(self):
	# 	try:
	# 		output_pointer = open("builds/%s") %(self.target_skeleton)
	# 		output_pointer.write(self.file_contents)
	# 		output_pointer.close()
	# 		print(commonUtils.color("Generated output file: ", status=True), + "%s") %(commonUtils.color(str(output_pointer.name), status=False, yellow=True))
	# 	except Exception as e:
	# 		print (commonUtils.color(("Error generating output file %s: " %(str(self.target_skeleton))), warning=True, status=False) + "%s") % (str(e))
	# 		pass


# Sample usage ---- # TODO; # DEBUG; # NEPHEW, DELETE DIS
# file_contents = 'msg = "this is a test of the emergency broacdcast system"\nfoo = ```[var:::foo]```\nbar = \'```[var:::bar]```\'\n\n#Here is some code\nprint foo\nprint bar\nprint msg\nprint ```[var:::foo]```\n'
# target_var = "foo"
# new_value = r"ayyyyylmao"

# s = VarReplacer(file_contents, target_var, new_value)
# print "Does target_var match s.target_var?: %s" %(target_var == s.target_var)
# s.ReplaceString()
# print "File was modified?: %s" %(s.file_contents != file_contents)
