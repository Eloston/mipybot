class handler():
    def __init__(self, *args):
        self.NAME = "Template"
        self.HEADER = 0x00

    def send(self, roboclass):
        print("Sending not defined in", self.NAME)
        # Make sure all data that is needed to be sent is returned.
        # Also make note that the header will be added in when sent.

    def receive(self, roboclass):
        # This function will get the length of every byte of a Minecraft packet, and parse the packet's data. This doesn't include the header.
        # The return of this function will be the length of the packet.
        # All packet handlers must at least implement this if it is designed to be received by the client
        print("Recieving not defined in", self.NAME)
