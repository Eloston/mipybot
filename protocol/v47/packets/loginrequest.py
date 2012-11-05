from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Login Request"
        self.HEADER = 0x01

    def receive(self, roboclass):
        entityid = roboclass.PACKETS.POINTER.read('int')

        leveltype = roboclass.PACKETS.POINTER.read('string')

        gamemode = roboclass.PACKETS.POINTER.read('byte')

        dimension = roboclass.PACKETS.POINTER.read('byte')

        difficulty = roboclass.PACKETS.POINTER.read('byte')

        unused = roboclass.PACKETS.POINTER.read('ubyte') # Seems to be only 0

        maxplayers = roboclass.PACKETS.POINTER.read('ubyte')

        roboclass.CHARACTER.ENTITYID = entityid
        roboclass.NETWORK.MAXPLAYERS = maxplayers
        worldinfodict = dict()
        worldinfodict['leveltype'] = leveltype
        worldinfodict['dimension'] = dimension
        worldinfodict['gamemode'] = gamemode
        worldinfodict['difficulty'] = difficulty
        roboclass.CHARACTER.updateworldinfo(worldinfodict)

        print("Login Information:\nEntity ID: ", entityid, "\nLevel Type: ", leveltype, "\nGame mode: ", gamemode, "\nDimension: ", dimension, "\nDifficulty: ", difficulty, "\nUnused: ", unused, "\nMax Players: ", maxplayers, "\n--------------------")

        return roboclass.PACKETS.POINTER.getposition()
