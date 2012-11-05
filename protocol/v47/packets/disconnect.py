from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Disconnect/Kick"
        self.HEADER = 0xFF
    def send(self, roboclass):
        return b'\x00\x00' # This is a short of zero, which means there is a zero length string following. Usually when we send this it's when the client wants to disconnect.

    def receive(self, roboclass):
        disconnectmessage = roboclass.PACKETS.POINTER.read('string')
        print("Disconnect/Kick message:", disconnectmessage)
        roboclass.SIGNALS.emit("stop")
        return roboclass.PACKETS.POINTER.getposition()
