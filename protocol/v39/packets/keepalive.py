from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Keep Alive"
        self.HEADER = 0x00
        self.KEEPALIVE = None # Bytes object of the latest Keep Alive information from the server

    def send(self, roboclass):
        return self.KEEPALIVE

    def receive(self, roboclass, data):
        self.KEEPALIVE = data
        roboclass.PACKETS.send(0x00)

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.INTEGER_LENGTH # There's only an integer in the Keep Alive packet
