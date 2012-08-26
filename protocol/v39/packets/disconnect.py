from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Disconnect/Kick"
        self.HEADER = 0xFF
    def send(self, roboclass):
        return b'\x00\x00' # This is a short of zero, which means there is a zero length string following. Usually when we send this it's when the client wants to disconnect.

    def receive(self, roboclass, data):
        disconnectmessage = roboclass.CONVERTER.getstringdata(data)["string"]
        print("Disconnect/Kick message:", disconnectmessage)
        roboclass.stop()

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.SHORT_LENGTH+roboclass.CONVERTER.getstringdata(data)["length"]
