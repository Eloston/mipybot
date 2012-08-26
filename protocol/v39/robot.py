import socket
import struct
import threading
import time
from . import library

class main():
    def __init__(self):
        packets = __import__("packets", globals=globals(), locals=locals())
        self.PACKETS = packets.handlermanager(self)
        self.PACKETS.initiatehandlers()

        self.CONVERTER = library.converter()

        self.ENCRYPTION = library.encryption()

        self.CHARACTER = character()

        self.NETWORK = network(self)

        self.STOPPING = False # Whether the robot is shutting down or not

    def start(self):
        '''
        Start the robot
        '''
        self.NETWORK.start()

    def stop(self):
        '''
        Stop the robot
        '''
        self.NETWORK.stop()

class character():
    def __init__(self):
        self.ISDEAD = False
        self.ENTITYID = None # Players Entity ID
        self.WORLDINFO = {"leveltype": None, "gamemode": 0, "dimension": 0, "difficulty": 0, "maxheight": 256}
        self.POSITION = {'x': 0, 'y': 0, 'z': 0, 'yaw': 0, 'pitch': 0}
        self.HEALTH = {'hp': 0, 'food': 0, 'foodsaturation': 0.0}
        self.TIME = 0 # Time in ticks
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

class network():
    def __init__(self, roboclass):
        self.LISTENTHREAD = threading.Thread(target=self.listen)
        self.SOCKET = None
        self.PROTOCOL = 39
        self.HOST = None
        self.PORT = 25565
        self.SERVER_DISCONNECT = False # Determines if the server disconnected the robot
        self.ROBOCLASS = roboclass
        self.MAXPLAYERS = None # Max players on server integer

    def start(self):
        self.ROBOCLASS.ENCRYPTION.generateAES()
        self.SOCKET = socket.socket()
        self.SOCKET.connect((self.HOST, self.PORT))
        self.LISTENTHREAD.start()
        self.ROBOCLASS.PACKETS.send(0x02)

    def stop(self):
        self.ROBOCLASS.STOPPING = True
        self.LISTENTHREAD.join()
        if not self.SERVER_DISCONNECT:
            self.ROBOCLASS.PACKETS.send(0xFF)
        self.SOCKET.close()

    def send(self, data):
        if not self.ROBOCLASS.STOPPING:
            if self.ROBOCLASS.ENCRYPTION.ENCRYPTION_ENABLED:
                data = self.ROBOCLASS.ENCRYPTION.AESencrypt(data)
            self.SOCKET.send(data)

    def receive(self, data):
        if self.ROBOCLASS.ENCRYPTION.ENCRYPTION_ENABLED:
            data = self.ROBOCLASS.ENCRYPTION.AESdecrypt(data)
            print("Decrpyted data!")
        self.ROBOCLASS.PACKETS.process(data)

    def listen(self):
        while True:
            if self.ROBOCLASS.STOPPING:
                break
            else:
                receivebytes = self.SOCKET.recv(4096)
                if len(receivebytes) == 0:
                    time.sleep(0.1)
                else:
                    self.receive(receivebytes)
