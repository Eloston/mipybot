class handler():
    def __init__(self, *args):
        self.NAME = "Template"
        self.HEADER = 0x00
    def send(self, roboclass):
        print("Sending not defined in", self.NAME)
        # Make sure all data that is needed to be sent is returned.
        # Also make note that the header will be added in when sent.
    def receive(self, roboclass, data):
        # This function's return will not go anywhere.
        # Make note that the header is stripped out from the packet
        print("Recieving not defined in", self.NAME)
    def getlength(self, roboclass, data):
        # This function will get the length of every byte of a Minecraft packet. This doesn't include the header.
        # Make sure the final length is returned.
        # All packet handlers must at least this implemented if it is designed to be received by the client
        print("Getting length not implemented in", self.NAME)
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("Data:", data)
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
