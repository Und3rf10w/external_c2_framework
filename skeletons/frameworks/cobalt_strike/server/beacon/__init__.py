class Beacon(object):
    def __init__(self):
        self.sock = ""
        self.beacon_id = ""
        # Default to a block time of 30 seconds
        self.block_time = 30


