from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Plugin Message"
        self.HEADER = 0xFA

    def receive(self, roboclass):
        channel = roboclass.PACKETS.POINTER.read('string')
        print("Plugin channel:", channel)
        roboclass.PACKETS.POINTER.read('shortdata')

        return roboclass.PACKETS.POINTER.getposition()
