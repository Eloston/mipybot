from yapsy.IPlugin import IPlugin

class autorespawn(IPlugin):
    def __init__(self):
        self.ROBOCLASS = None

    def getPluginAPIversion(self):
        return "0.1"

    def setRoboclass(self, roboclass):
        self.ROBOCLASS = roboclass

    def activate(self):
        self.ROBOCLASS.NETWORK.PACKETS.PACKETSIGNALS.getsignal(0x08).addreceiver(self.checkRespawn)

    def checkRespawn(self):
        '''
        Checks if the robot is dead via HP level and respawns robot if so.
        '''
        if self.ROBOCLASS.CHARACTER.HEALTH < 1:
            print("Respawning...")
            self.ROBOCLASS.NETWORK.PACKETS.send(0xCD)
