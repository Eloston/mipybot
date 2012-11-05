import struct
import threading
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

class converter():
    def __init__(self):
        self.SHORT_LENGTH = 2 # The length of a short in bytes
        self.INTEGER_LENGTH = 4 # The length of a integer in bytes
        self.LONG_LENGTH = 8 # The length of a long (a long long) in bytes
        self.DOUBLE_LENGTH = 8 # The length of a double in bytes
        self.FLOAT_LENGTH = 4 # The length of a float in bytes
        self.BYTE_LENGTH = 1 # The length of a byte
        self.STRING_ENCODE = "UTF-16be"

    def getshort(self, data, offset=0, signed=True):
        '''
        Returns a Python integer from a Minecraft short
        '''
        if signed:
            formatstring = '!h'
        else:
            formatstring = '!H'
        return struct.unpack(formatstring, data[offset:offset+self.SHORT_LENGTH])[0]

    def makeshort(self, value, signed=True):
        '''
        Returns a Minecraft short from a Python integer
        '''
        if signed:
            formatstring = '!h'
        else:
            formatstring = '!H'
        return struct.pack(formatstring, value)

    def getshortdata(self, data, offset=0, doublelength=False):
        '''
        Returns the dictionary of the short value and the data following the short.
        Many packets in Minecraft have data where a short determines the length of the data following.
        '''
        length = self.getshort(data, offset)
        if doublelength:
            length *= 2
        offset += self.SHORT_LENGTH
        newdata = data[offset:offset+length]
        return {"length": length, "data": newdata}

    def getstringdata(self, data, offset=0):
        '''
        Returns the python string format of the Minecraft string and the length of the string in bytes.
        This returns a dictionary of these values.
        '''
        shortdatadict = self.getshortdata(data, offset, True)
        return {"length": shortdatadict["length"], "string": shortdatadict["data"].decode(self.STRING_ENCODE)}

    def makestring(self, string):
        '''
        Returns a string in Minecraft's format
        '''
        shortlength = struct.pack('!h', len(string))
        bytestring = string.encode(self.STRING_ENCODE)
        return shortlength + bytestring

    def getbyte(self, data, offset=0, signed=False):
        '''
        Converts a byte into a Python integer
        '''
        if signed:
            formatstring = 'b'
        else:
            formatstring = 'B'
        return struct.unpack(formatstring, data[offset:offset+self.BYTE_LENGTH])[0]

    def makebyte(self, value, signed=False):
        '''
        Converts a Python integer into a byte
        '''
        if signed:
            formatstring = 'b'
        else:
            formatstring = 'B'
        return struct.pack(formatstring, value)

    def getbool(self, data, offset=0):
        '''
        Converts a Minecraft boolean into a Python boolean
        '''
        byte = self.getbyte(data, offset)
        if byte == 0x01:
            return True
        elif byte == 0x00:
            return False
        else:
            return None

    def makebool(self, value):
        '''
        Converts a Python boolean into a Minecraft boolean
        '''
        if value:
            return self.makebyte(0x01)
        else:
            return self.makebyte(0x00)

    def getinteger(self, data, offset=0, signed=True):
        '''
        Returns a python integer from a Minecraft integer
        '''
        if signed:
            formatstring = '!i'
        else:
            formatstring = '!I'
        return struct.unpack(formatstring, data[offset:offset+self.INTEGER_LENGTH])[0]

    def makeinteger(self, value, signed=True):
        '''
        Returns a Minecraft integer from a python integer
        '''
        if signed:
            formatstring = '!i'
        else:
            formatstring = '!I'
        return struct.pack(formatstring, value)

    def getintegerdata(self, data, offset=0):
        '''
        Returns the dictionary of the integer value and the data following the integer.
        Some packets in Minecraft have data where a integer determines the length of the data following.
        '''
        length = self.getinteger(data, offset)
        offset += self.INTEGER_LENGTH
        newdata = data[offset:offset+length]
        return {"length": length, "data": newdata}

    def getlong(self, data, offset=0, signed=True):
        '''
        Returns a Python integer from a Minecraft long
        '''
        if signed:
            formatstring = '!q'
        else:
            formatstring = '!Q'
        return struct.unpack(formatstring, data[offset:offset+self.LONG_LENGTH])[0]

    def makelong(self, value, signed=True):
        '''
        Returns a Minecraft long from a python integer
        '''
        if signed:
            formatstring = '!q'
        else:
            formatstring = '!Q'
        return struct.pack(formatstring, value)

    def getfloat(self, data, offset=0):
        '''
        Returns a Python float from a Minecraft float
        '''
        return struct.unpack('!f', data[offset:offset+self.FLOAT_LENGTH])[0]

    def makefloat(self, value):
        '''
        Returns a Minecraft float from a Python float
        '''
        return struct.pack('!f', value)

    def getdouble(self, data, offset=0):
        '''
        Returns a Python float from a Minecraft double
        '''
        return struct.unpack('!d', data[offset:offset+self.DOUBLE_LENGTH])[0]

    def makedouble(self, value):
        '''
        Returns a Minecraft double from a Python float
        '''
        return struct.pack('!d', value)

class encryption():
    def __init__(self):
        self.ENCRYPTION_ENABLED = False
        # The AES cipher instance must be different, but to create them is the same.
        self.AESCIPHERENC = None
        self.AESCIPHERDEC = None
        self.AESKEY = None # When defined, it will not be encoded with the server's public key
        self.PKCSCIPHER = None
        self.SERVERID = None
        self.PUBLICKEY = None # When a different value goes in here, it will be the server's public key in ASN.1 defined by X.509
        self.VERIFICATIONTOKEN = None

    def generateAES(self):
        '''
        Generates the AES key, encrypting cipher, and decrypting cipher
        '''
        self.AESKEY = Crypto.Random.new().read(AES.block_size)
        self.AESCIPHERENC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)
        self.AESCIPHERDEC = AES.new(self.AESKEY, AES.MODE_CFB, self.AESKEY)

    def makePKCSCIPHER(self, encodedkey):
        '''
        Decodes a public key from the input into ASN.1 format defined by X.509, and generates a PKCS v1.5 cipher
        '''
        self.PUBLICKEY = RSA.importKey(encodedkey)
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
        return self.AESCIPHERENC.encrypt(data)

    def AESdecrypt(self, data):
        '''
        Decrypts data witht he symnetric key
        '''
        return self.AESCIPHERDEC.decrypt(data)

class signals():
    def __init__(self):
        '''
        The Signal Dictionary Format
        ============================
        self.SIGNALDICT is the dictionary that contains all the different signals
        Each key in self.SIGNALDICT contains another dictionary containing the receiver information.

        The format of the receiver dictionary is NAME: FUNCTION.
        NAME is a label that refers to that specific function to be called when the signal is emitted.
        FUNCTION refers to a function template NOT instance. For example, if you define a function foo() in the class bar(), then you would refer to it in the receiver dictionary as bar.foo
        '''
        self.SIGNALDICT = dict()
        self.SIGNALTHREADS = list() # Contains a list of thread classes for signal receiver execution.

    def checksignalname(self, signame):
        '''
        Checks to see if the signal name signame has already been defined
        '''
        if signame in iter(self.SIGNALDICT.keys()):
            return True
        else:
            return False

    def checkreceivername(self, signame, receivername):
        '''
        Checks to see if the receiver receivername has already been defined in the signal signame
        '''
        if self.checksignalname(signame):
            if receivername in iter(self.SIGNALDICT[signame].keys()):
                return True
            else:
                return False
        else:
            raise Exception(' '.join(['Signal', signame, 'does not exist.']))

    def newsignal(self, signame):
        '''
        Creates a new signal signame if it does not already exist.
        '''
        if self.checksignalname(signame):
            raise Exception(' '.join(['Signal', signame, 'already exists.']))
        else:
            self.SIGNALDICT[signame] = dict()

    def delsignal(self, signame):
        '''
        Deletes an existing signal signame. Deletes all receiver information as well.
        '''
        if self.checksignalname(signame):
            del self.SIGNALDICT[signame]
        else:
            raise Exception(' '.join(['Signal', signame, 'does not exist.']))

    def newreceiver(self, signame, receivername, receiverfunction):
        '''
        Creates a new receiver with function receiverfunction and name receivername in the signal signame if it does not already exist.
        '''
        if self.checkreceivername(signame, receivername):
            raise Exception(' '.join(['Signal receiver', receivername, 'already exists.']))
        else:
            self.SIGNALDICT[signame][receivername] = receiverfunction

    def delreceiver(self, signame, receivername):
        '''
        Deletes an existing receiver receivername in signal signame
        '''
        if self.checkreceivername(signame, receivername):
            del self.SIGNALDICT[signame][receivername]
        else:
            raise Exception(' '.join(['Signal receiver', receivername, 'does not exist.']))

    def iteratereceivers(self, signame):
        '''
        Iterates and executes all receivers in signal signame
        It is recommended to use emit to call this instead.
        '''
        receiverfunctions = iter(self.SIGNALDICT[signame].values())
        for receiver in receiverfunctions:
            receiver()

    def checksignalthreadactivity(self):
        '''
        Checks for signal threads where execution has ended and remove them
        '''
        for signalthread in self.SIGNALTHREADS:
            if not signalthread.is_alive():
                self.SIGNALTHREADS.remove(signalthread)

    def emit(self, signame, separatethread=True):
        '''
        Runs all functions under signame.
        separatethread determines if the execution of the receivers will be done on a separate thread or not. Defaults to true
        '''
        if separatethread:
            newthread = threading.Thread(kwargs={"signame": signame}, target=self.iteratereceivers)
            self.SIGNALTHREADS += [newthread]
            newthread.start()
            self.checksignalthreadactivity()
        else:
            self.iteratereceivers(signame)
