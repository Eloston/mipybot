from . import template

class handler():
    def __init__(self, *args):
        self.NAME = "Client Statuses"
        self.HEADER = 0xCD

    def send(self, roboclass):
        if roboclass.ISDEAD:
            return b'\x01'
        else:
            # This must be the initial spawn if we send this but we're not dead
            return b'\x00'
