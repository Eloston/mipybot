from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Set Experience"
        self.HEADER = 0x2B

    def receive(self, roboclass):
        xpdict = dict()

        xpdict['bar'] = roboclass.PACKETS.POINTER.read('float')

        xpdict['level'] = roboclass.PACKETS.POINTER.read('short')

        xpdict['total'] = roboclass.PACKETS.POINTER.read('short')

        roboclass.CHARACTER.updateexperience(xpdict)

        print("Experience dictionary:", xpdict)

        return roboclass.PACKETS.POINTER.getposition()
