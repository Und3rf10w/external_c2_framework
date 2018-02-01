import re

class VarReplacer(object):
	def __init__(self, target_file, target_var, new_value):
		self.new_value = new_value #given as `r'\\.\sample\unescaped\string'` (sans grave accents, include quotes) if str; if a number, just give the number
		self.target_file = target_file
		self.regex_replacement_marker = '```\[var:::(\w*)\]```'
		self.regex_replacement_value_marker = '```\[var:::'+self.new_value+'\]```' 
		self.target_var = target_var # given as a normal string
	
	def ReplaceString(self):
		replace_string = list(set(re.findall(self.regex_replacement_marker, self.target_file)))
		for var in replace_string:
			if isinstance(self.new_value, (int, long, float, complex)):
				self.target_file = re.sub(self.regex_replacement_value_marker.replace(str(self.new_value), self.target_var), str(self.new_value), self.target_file)
			else:
				self.target_file = re.sub(self.regex_replacement_value_marker.replace(str(self.new_value), self.target_var), repr(str(self.new_value)), self.target_file)
	
	def GetCurrentFile(self):
		return self.target_file


# Sample usage ---- # TODO; # DEBUG; # NEPHEW, DELETE DIS
# target_file = 'msg = "this is a test of the emergency broacdcast system"\nfoo = ```[var:::foo]```\nbar = \'```[var:::bar]```\'\n\n#Here is some code\nprint foo\nprint bar\nprint msg\nprint ```[var:::foo]```\n'
# target_var = "foo"
# new_value = r"ayyyyylmao"

# s = VarReplacer(target_file, target_var, new_value)
# print "Does target_var match s.target_var?: %s" %(target_var == s.target_var)
# s.ReplaceString()
# print "File was modified?: %s" %(s.target_file != target_file)
