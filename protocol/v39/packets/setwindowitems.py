from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Window Items"
        self.HEADER = 0x68

    def receive(self, roboclass):
        roboclass.PACKETS.POINTER.read('byte')
        count = roboclass.PACKETS.POINTER.read('short')
        # Reading the slot array
        parsed = 1 # Because when we enter the while loop, it would've already parsed one
        while parsed <= count:
            roboclass.PACKETS.POINTER.read('slot')
            parsed += 1

        return roboclass.PACKETS.POINTER.getposition()
