"""
Common messages
"""

import helpers

version = "0.0.1a"


def title():
	"""
	Print the framework title, with version
	"""

	print '==========================================='
	print ' %s | VERSION: %s' % (helpers.color('ExternalC2Gen',status=False,bold=True), version)
	print '==========================================='
	print 'Created by @Und3rf10w, released to you with <3'
	print '==========================================='

