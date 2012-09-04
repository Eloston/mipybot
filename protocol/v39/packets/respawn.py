from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Respawn"
        self.HEADER = 0x09

    def receive(self, roboclass):
        dimension = roboclass.PACKETS.POINTER.read('int')

        difficulty = roboclass.PACKETS.POINTER.read('byte')

        gamemode = roboclass.PACKETS.POINTER.read('byte')

        worldheight = roboclass.PACKETS.POINTER.read('short')

        leveltype = roboclass.PACKETS.POINTER.read('string')

        worldinfodict = dict()
        worldinfodict['dimension'] = dimension
        worldinfodict['difficulty'] = difficulty
        worldinfodict['gamemode'] = gamemode
        worldinfodict['maxheight'] = worldheight
        worldinfodict['leveltype'] = leveltype
        roboclass.CHARACTER.updateworldinfo(worldinfodict)

        return roboclass.PACKETS.POINTER.getposition()
