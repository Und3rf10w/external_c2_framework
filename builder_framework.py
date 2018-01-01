#!/usr/bin/env/python2

import sys, argparse, socket

from modules.common import helpers
from modules.common import messages

if __name__ == '__main__':
	try:

		parser = argparse.ArgumentParser()
		parser.add_argument('-v', action='store_true', help='Enable verbose output', dest='verbose')

		# Call arguments with args.$ARGNAME
		args = parser.parse_args()

		# Print the title
		messages.title()


	# Catch ctrl + c interrupts from the user
	except KeyboardInterrupt:
		print helpers.color("\n Exiting...", warning=True)

	except EOFError:
		print helpers.color("\n Exiting...", warning=True)