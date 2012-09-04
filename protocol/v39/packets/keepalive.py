from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Keep Alive"
        self.HEADER = 0x00
        self.KEEPALIVE = None # Bytes object of the latest Keep Alive information from the server

    def send(self, roboclass):
        return roboclass.CONVERTER.makeinteger(self.KEEPALIVE)

    def receive(self, roboclass):
        self.KEEPALIVE = roboclass.PACKETS.POINTER.read('int')
        print("Keep Alive number:", self.KEEPALIVE)
        roboclass.PACKETS.send(0x00)

        return roboclass.PACKETS.POINTER.getposition()
