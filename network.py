import constants
import packets

import socket
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
import threading
import time

class encryption():
    def __init__(self):
        self.AESCIPHER_DEC = None
        self.AESCIPHER_ENC = None
        self.AESKEY = None
        self.PKCSCIPHER = None
        self.ENCODEDPUBLICKEY = None
        self.PUBLICKEY = None
        self.VERIFICATIONTOKEN = None
        self.ENCRYPTION_ENABLED = False

    def generateAES(self):
        '''
        Generates the AES key, encrypting cipher, and decrypting cipher
        '''
        self.AESKEY = Crypto.Random.new().read(AES.block_size)
        self.AESCIPHER_ENC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)
        self.AESCIPHER_DEC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)

    def makePKCSCIPHER(self):
        '''+
        Decodes a public key from the input into ASN.1 format defined by X.509, and generates a PKCS v1.5 cipher
        '''
        self.PUBLICKEY = RSA.importKey(self.ENCODEDPUBLICKEY)
        self.PKCSCIPHER = PKCS1_v1_5.new(self.PUBLICKEY)

    def PKCSencrypt(self, data):
        '''
        Encrypts data with the server's public key
        '''
        return self.PKCSCIPHER.encrypt(data)

    def AESencrypt(self, data):
        '''
        Encrypts data with the symnetric key
        '''
        return self.AESCIPHER_ENC.encrypt(data)

    def AESdecrypt(self, data):
        '''
        Decrypts data witht he symnetric key
        '''
        return self.AESCIPHER_DEC.decrypt(data)

class connection():
    def load(self, roboclass):
        self.ROBOCLASS = roboclass
        self.ENCRYPTION = encryption()
        self.SOCKET = None

    def start(self):
        self.SOCKET = socket.socket()
        self.SOCKET.connect((self.ROBOCLASS.HOST, self.ROBOCLASS.PORT))

    def send(self, data):
        if self.ENCRYPTION.ENCRYPTION_ENABLED:
            data = self.ENCRYPTION.AESencrypt(data)
        self.SOCKET.send(data)

    def read(self):
        data = b''
        while len(data) == 0:
            data = self.SOCKET.recv(constants.Socketbuffer)
            time.sleep(0.00001)
        if self.ENCRYPTION.ENCRYPTION_ENABLED:
            data = self.ENCRYPTION.AESdecrypt(data)
        return data

class sendbuffer():
    def load(self, roboclass):
        self.BUFFER = bytes()
        self.CONNECTION = roboclass.NETWORK.CONNECTION

    def add(self, data):
        self.BUFFER += data

    def clear(self):
        self.BUFFER = bytes()

    def flush(self):
        self.CONNECTION.send(self.BUFFER)
        self.clear()

class receivebuffer():
    def load(self, roboclass):
        self.BUFFER = bytes()
        self.CONNECTION = roboclass.NETWORK.CONNECTION

    def read(self):
        '''
        Reads new data from the socket buffer and adds it to this buffer
        '''
        self.BUFFER += self.CONNECTION.read()

    def checkbufferlength(self, length):
        '''
        Checks if current buffer needs to be updated to match length "length"
        '''
        while len(self.BUFFER) < length:
            self.read()

    def pop(self, length):
        '''
        Reads "length" number of bytes and deletes it from the buffer
        '''
        self.checkbufferlength(length)
        request = self.BUFFER[:length]
        self.BUFFER = self.BUFFER[length:]
        return request

class network():
    def load(self, roboclass):
        self.ROBOCLASS = roboclass
        self.CONNECTION = connection()
        self.CONNECTION.load(roboclass)
        self.SENDBUFFER = sendbuffer()
        self.SENDBUFFER.load(roboclass)
        self.RECEIVEBUFFER = receivebuffer()
        self.RECEIVEBUFFER.load(roboclass)
        self.PACKETS = packets.manager()
        self.PACKETS.load(roboclass)
        self.LISTENTHREAD = threading.Thread(target=self.listenthread)
        self.SENDTHREAD = threading.Thread(target=self.sendthread)
        self.SENDTHREAD.daemon = True

    def start(self):
        self.CONNECTION.start()
        self.PACKETS.start()
        self.LISTENTHREAD.start()
        self.SENDTHREAD.start()

    def listenthread(self):
        while not self.ROBOCLASS.STOPPING:
            self.PACKETS.read_iteration()

    def sendthread(self):
        while not self.ROBOCLASS.STOPPING:
            self.PACKETS.send_iteration()
