from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Change Game State"
        self.HEADER = 0x46

    def receive(self, roboclass, data):
        reason = roboclass.CONVERTER.getbyte(data)
        Position = roboclass.CONVERTER.BYTE_LENGTH
        gamemode = roboclass.CONVERTER.getbyte(data, Position)
        Position += roboclass.CONVERTER.BYTE_LENGTH
        reasonstring = ''
        reasondict = dict()
        reasondict[0] = "Invalid Bed"
        reasondict[1] = "Begin raining"
        reasondict[2] = "End raining"
        reasondict[3] = "Change game mode"
        reasondict[4] = "Enter credits"
        try:
            reasonstring = reasondict[reason]
            print("Got reason", reasonstring, "number", reason)
        except:
            print("Unknown reason", reason)

        roboclass.CHARACTER.updateworldinfo({'gamemode': gamemode})
        print("Gamemode is", gamemode)

    def getlength(self, roboclass, data):
        return 2
