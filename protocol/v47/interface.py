class template():
    def __init__(self, roboclass):
        self.roboclass = roboclass

class status(template):
    def respawn(self):
        if roboclass.CHARACTER.ISDEAD:
            roboclass.PACKETS.send(0xCD)

class main():
    def __init__(self, roboclass):
        self.status = status(roboclass)
