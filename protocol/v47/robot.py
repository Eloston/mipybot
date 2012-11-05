import socket
import threading
import time
from . import library
from . import interface
from .version import PROTOCOLVERSION

class main():
    def __init__(self):
        packets = __import__("packets", globals=globals(), locals=locals())
        self.PACKETS = packets.handlermanager(self)
        self.PACKETS.initiatehandlers()

        self.ROBOLIB = library

        self.CONVERTER = self.ROBOLIB.converter()

        self.ENCRYPTION = self.ROBOLIB.encryption()

        self.CHARACTER = self.ROBOLIB.character()

        self.NETWORK = self.ROBOLIB.network(self)

        self.STOPPING = False # Whether the robot is shutting down or not

        self.SIGNALS = self.ROBOLIB.signals()

        self.SIGNALS.newsignal("stop")
        self.SIGNALS.newreceiver("stop", "roboclass.stop", self.stop)

        self.INTERFACE = interface

    def start(self):
        '''
        Start the robot
        '''
        print("Staring the robot...")
        self.NETWORK.start()

    def stop(self):
        '''
        Stop the robot
        '''
        self.STOPPING = True
        print("Stopping the robot...")
        self.NETWORK.stop()
        print("Stopping complete")

class character():
    def __init__(self):
        self.ISDEAD = False
        self.ENTITYID = None # Players Entity ID
        self.WORLDINFO = {"leveltype": None, "gamemode": 0, "dimension": 0, "difficulty": 0, "maxheight": 256}
        self.POSITION = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'yaw': 0.0, 'pitch': 0.0, 'stance': 0.0, 'onground': False}
        self.HEALTH = {'hp': 0, 'food': 0, 'foodsaturation': 0.0}
        self.EXPERIENCE = {'bar': 0, 'level': 0, 'total': 0}
        self.TIMEAGE = 0 # The time since the creation of the world
        self.TIMEDAY = 0 # Time of day
        self.USERNAME = None

    def updateworldinfo(self, newinfodict):
        '''
        Update the world info
        '''
        for item in list(newinfodict.keys()):
            self.WORLDINFO[item] = newinfodict[item]

    def updateposition(self, newinfodict):
        for item in list(newinfodict.keys()):
            self.POSITION[item] = newinfodict[item]

    def updatehealth(self, newinfodict):
        for item in list(newinfodict.keys()):
            self.HEALTH[item] = newinfodict[item]

        if self.HEALTH['hp'] <= 0:
            self.ISDEAD = True
        else:
            self.ISDEAD = False

    def updateexperience(self, newinfodict):
        for item in list(newinfodict.keys()):
            self.EXPERIENCE[item] = newinfodict[item]

class network():
    def __init__(self, roboclass):
        self.LISTENTHREAD = threading.Thread(target=self.listen)
        self.SOCKET = None
        self.PROTOCOL = PROTOCOLVERSION[0]
        self.HOST = None
        self.PORT = 25565
        self.SERVER_DISCONNECT = False # Determines if the server disconnected the robot
        self.ROBOCLASS = roboclass
        self.MAXPLAYERS = None # Max players on server integer
        #self.SOCKETBUFFER = 2**25
        self.SOCKETBUFFER = 4096
        self.PACKETDATA = bytes() # Holds packet data comming from the server.

    def start(self):
        self.ROBOCLASS.ENCRYPTION.generateAES()
        self.SOCKET = socket.socket()
        self.SOCKET.connect((self.HOST, self.PORT))
        self.LISTENTHREAD.start()
        self.ROBOCLASS.PACKETS.send(0x02)

    def stop(self):
        #self.LISTENTHREAD.join()
        if not self.SERVER_DISCONNECT:
            self.ROBOCLASS.PACKETS.send(0xFF)
        self.SOCKET.close()

    def send(self, data):
        if not self.ROBOCLASS.STOPPING:
            if self.ROBOCLASS.ENCRYPTION.ENCRYPTION_ENABLED:
                data = self.ROBOCLASS.ENCRYPTION.AESencrypt(data)
            self.SOCKET.send(data)

    def listen(self):
        while True:
            if self.ROBOCLASS.STOPPING:
                break
            else:
                self.PACKETDATA = bytes()
                self.receive()
                self.ROBOCLASS.PACKETS.process()

    def receive(self):
        while True:
            receivebytestemp = self.SOCKET.recv(self.SOCKETBUFFER)
            if self.ROBOCLASS.ENCRYPTION.ENCRYPTION_ENABLED:
                data = self.ROBOCLASS.ENCRYPTION.AESdecrypt(receivebytestemp)
                print("Decrpyted data!")
            else:
                data = receivebytestemp
            self.PACKETDATA += data
            if len(receivebytestemp) == self.SOCKETBUFFER:
                print("***WARNING: RECEIVED DATA LENGTH IS EQUIVALENT TO SOCKET RECEIVE BUFFER VALUE***")
            else:
                break
