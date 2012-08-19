import socket
import struct
import binascii
import threading
import time
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

class base_robot():
    def __init__(self):
        self.PACKETS = __import__("packets", globals=globals(), locals=locals())
        self.PACKETS.initiatehandlers()
        self.USERNAME = None
        self.HOST = None
        self.PORT = 25565
        self.STRING_ENCODE = "UTF-16be"
        self.SOCKET = None
        self.ENCRYPTION_ENABLED = False
        # The AES cipher instance must be different, but to create them is the same.
        self.AESCIPHERENC = None
        self.AESCIPHERDEC = None
        self.AESKEY = None # When defined, it will not be encoded with the server's public key
        self.SHORT_LENGTH = 2 # The length of a short in bytes
        self.INTEGER_LENGTH = 4 # The length of a integer in bytes
        self.PROTOCOL = 39
        self.LISTENTHREAD = threading.Thread(target=self.listen)
        self.STOPPING = False # Whether the robot is shutting down or not
        self.PKCSCIPHER = None
        self.ENCRYPTIONREQUESTLIST = None # The Server ID, Public Key, and Verification Token list.
        self.ISDEAD = False

    def generateAES(self):
        self.AESKEY = Crypto.Random.new().read(AES.block_size)
        self.AESCIPHERENC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)
        self.AESCIPHERDEC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)

    def start(self):
        self.generateAES()
        self.SOCKET = socket.socket()
        self.SOCKET.connect((self.HOST, self.PORT))
        self.LISTENTHREAD.start()
        self.PACKETS.senddata(self, 0x02)

    def stop(self):
        self.STOPPING = True
        self.LISTENTHREAD.join()

    def socketsend(self, data):
        if not self.STOPPING:
            if self.ENCRYPTION_ENABLED:
                data = self.AESCIPHERENC.encrypt(data)
            self.SOCKET.send(data)

    def socketreceive(self, data):
        if self.ENCRYPTION_ENABLED:
            data = self.AESCIPHERDEC.decrypt(data)
            print("Decrpyted data!")
        self.PACKETS.processdata(self, data)

    def listen(self):
        while True:
            if self.STOPPING:
                break
            else:
                receivebytes = self.SOCKET.recv(4096)
                if len(receivebytes) == 0:
                    time.sleep(0.1)
                else:
                    self.socketreceive(receivebytes)
