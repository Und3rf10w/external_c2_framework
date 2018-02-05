def color(string, status=True, warning=False, bold=True, yellow=False):
	"""
	Change text color for the terminal, defaults to green

	Set "warning=True" for red
	"""

	attr = []

	if status:
		# green, probably will change this to default, I just use green normally.
		attr.append('32')
	if warning:
		# red
		attr.append('31')
	if bold:
		attr.append('1')
	if yellow:
		attr.append('33')
	return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)