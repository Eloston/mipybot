import os
import os.path
import sys
import struct
'''
Format for the packet handler dictionary:
{PacketID: HandlerObject}
Where PacketID is the packet header value, (such as 0xFD for Encryption Key Request), and HandlerObject is the packet handler object, derived from the handler() class
'''
class handlermanager():
    def __init__(self, roboclass):
        self.HANDLERDICT = dict()
        self.ROBOCLASS = roboclass
        self.WRAPPER = wrapper(roboclass)
        self.POINTER = pointer(roboclass)
        self.TYPES = types(roboclass)
        self.ROBOCLASS.SIGNALS.newsignal("PacketReceive")

    def initiatehandlers(self):
        exclude = ["__pycache__", "__init__.py", "__init__.pyc", "__init__.pyo", "template.py", "template.pyc", "template.pyo"]
        listing = os.listdir(os.path.dirname(__file__))
        for item in listing:
            if item in exclude:
                continue
            elif os.path.isdir(item):
                if '.' in item:
                    continue
            else:
                if os.path.isfile(os.path.join(os.path.dirname(__file__), item)):
                    if item.endswith(".pyc") or item.endswith(".pyo"):
                        item = item[:len(item)-4]
                    elif item.endswith(".py"):
                        item = item[:len(item)-3]
                    if '.' in item:
                        continue
                try:
                    tempdler = __import__(item, globals=globals(), locals=locals())
                    tempclass = tempdler.handler()
                    packetid = tempclass.HEADER
                    if packetid in self.HANDLERDICT:
                        print("***ERROR: SAME PACKET ALREADY LOADED***")
                        self.ROBOCLASS.SIGNALS.emit("stop")
                        exit()
                    else:
                        self.HANDLERDICT[packetid] = tempclass
                    del tempdler
                    del tempclass
                    del packetid
                except:
                    try:
                        del tempdler
                        del tempclass
                    except:
                        pass

    def gethandler(self, packetid):
        try:
            handler = self.HANDLERDICT[packetid]
        except:
            handler = None
        return handler

    def process(self):
        while len(self.ROBOCLASS.NETWORK.PACKETDATA) > 0:
            header = self.ROBOCLASS.CONVERTER.getbyte(self.ROBOCLASS.NETWORK.PACKETDATA)
            print("Got header", header, ",", hex(header))
            handclass = self.gethandler(header)
            if handclass == None:
                print("Unknown packet", hex(header))
                #print("Data:", data)
                self.ROBOCLASS.stop()
                break
            print("Received packet", handclass.NAME)
            self.ROBOCLASS.NETWORK.PACKETDATA = self.ROBOCLASS.NETWORK.PACKETDATA[self.ROBOCLASS.CONVERTER.BYTE_LENGTH:] # Strip out packet header
            self.POINTER.initpointer()
            packetdatalength = handclass.receive(self.ROBOCLASS)
            if len(self.ROBOCLASS.NETWORK.PACKETDATA) < packetdatalength:
                print("***ERROR: PACKET DATA LENGTH EXCEEDED DATA SIZE***")
                self.POINTER.checkbuffer(packetdatalength)
            self.ROBOCLASS.NETWORK.PACKETDATA = self.ROBOCLASS.NETWORK.PACKETDATA[packetdatalength:]
            if len(self.ROBOCLASS.NETWORK.PACKETDATA) == 0:
                print("***INFO: Data hit length of 0")
            '''
            packetdatalength = handclass.getlength(self.ROBOCLASS, self.ROBOCLASS.NETWORK.PAKETDATA)
            if packetdatalength > len(self.ROBOCLASS.NETWORK.PAKETDATA):
                print("***WARNING: CALCULATED PACKET LENGTH EXCEEDS LENGTH OF UNPROCESSED DATA***")
            packetdata = self.ROBOCLASS.NETWORK.PAKETDATA[:packetdatalength]
            self.ROBOCLASS.NETWORK.PAKETDATA = self.ROBOCLASS.NETWORK.PAKETDATA[packetdatalength:]
            if len(self.ROBOCLASS.NETWORK.PAKETDATA) == 0:
                print("***INFO: Data hit length of 0")
            handclass.receive(self.ROBOCLASS, packetdata)
            '''
        print("***INFO: Reached end of received data for packet processing***")

    def send(self, packetid):
        handclass = self.gethandler(packetid)
        print("Sending packet", handclass.NAME)
        tosend = handclass.send(self.ROBOCLASS)
        tosend = self.ROBOCLASS.CONVERTER.makebyte(handclass.HEADER)+tosend
        self.ROBOCLASS.NETWORK.send(tosend)

class wrapper():
    def __init__(self, roboclass):
        self.ROBOCLASS = roboclass

    def sendposition(self, sendlist):
        '''
        Determines which position packet to send (0x0A through 0x0D) according to a list of what needs to be sent to the server.
        The main point of this is to save some bandwidth.
        '''
        packetinfo = {0x0A: ['onground'], 0x0B: ['x', 'y', 'stance', 'z', 'onground'], 0x0C: ['yaw', 'pitch', 'onground'], 0x0D: ['x', 'y', 'stance', 'z', 'yaw', 'pitch', 'onground']}
        packetorder = [0x0A, 0x0C, 0x0B, 0x0D]
        for packetnum in packetorder:
            lastsucess = False
            templist = packetinfo[packetnum]
            for attribute in sendlist:
                if attribute in templist:
                    lastsucess = True
                else:
                    lastsucess = False
                    break
            if lastsucess:
                self.ROBOCLASS.PACKETS.send(packetnum)
                break

class pointer():
    def __init__(self, roboclass):
        self.ROBOCLASS = roboclass
        self.POSITION = None

    def checkbuffer(self, datasize=None):
        if datasize == None:
            datasize = self.POSITION
        while datasize > len(self.ROBOCLASS.NETWORK.PACKETDATA):
            self.ROBOCLASS.NETWORK.receive()

    def nickparse(self, string):
        signed = True
        string = string.lower()

        if string[:1] == "u":
            string = string[1:]
            signed = False

        if string == 'string':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.SHORT_LENGTH)
            stringlength = self.ROBOCLASS.CONVERTER.getshort(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION) * 2
            self.POSITION += self.ROBOCLASS.CONVERTER.SHORT_LENGTH
            self.checkbuffer(self.POSITION+stringlength)
            decodedstring = self.ROBOCLASS.CONVERTER.getstringdata(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION-self.ROBOCLASS.CONVERTER.SHORT_LENGTH)['string']
            self.POSITION += stringlength
            return decodedstring

        if string == 'shortdata':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.SHORT_LENGTH)
            datalength = self.ROBOCLASS.CONVERTER.getshort(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION)
            self.POSITION += self.ROBOCLASS.CONVERTER.SHORT_LENGTH
            self.checkbuffer(self.POSITION+datalength)
            data = self.ROBOCLASS.CONVERTER.getshortdata(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION-self.ROBOCLASS.CONVERTER.SHORT_LENGTH)['data']
            self.POSITION += datalength
            return data

        if string == 'integerdata':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.INTEGER_LENGTH)
            datalength = self.ROBOCLASS.CONVERTER.getinteger(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION)
            self.POSITION += self.ROBOCLASS.CONVERTER.INTEGER_LENGTH
            self.checkbuffer(self.POSITION+datalength)
            data = self.ROBOCLASS.CONVERTER.getintegerdata(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION-self.ROBOCLASS.CONVERTER.INTEGER_LENGTH)['data']
            self.POSITION += datalength
            return data

        elif string == 'byte':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.BYTE_LENGTH)
            if signed:
                data = self.ROBOCLASS.CONVERTER.getbyte(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, True)
            else:
                data = self.ROBOCLASS.CONVERTER.getbyte(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, False)
            self.POSITION += self.ROBOCLASS.CONVERTER.BYTE_LENGTH
            return data

        elif string == 'bool':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.BYTE_LENGTH)
            data = self.ROBOCLASS.CONVERTER.getbool(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION)
            self.POSITION += self.ROBOCLASS.CONVERTER.BYTE_LENGTH
            return data

        elif string == 'short':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.SHORT_LENGTH)
            if signed:
                data = self.ROBOCLASS.CONVERTER.getshort(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, True)
            else:
                data = self.ROBOCLASS.CONVERTER.getshort(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, False)
            self.POSITION += self.ROBOCLASS.CONVERTER.SHORT_LENGTH
            return data

        elif string == 'int':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.INTEGER_LENGTH)
            if signed:
                data = self.ROBOCLASS.CONVERTER.getinteger(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, True)
            else:
                data = self.ROBOCLASS.CONVERTER.getinteger(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, False)
            self.POSITION += self.ROBOCLASS.CONVERTER.INTEGER_LENGTH
            return data

        elif string == 'long':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.LONG_LENGTH)
            if signed:
                data = self.ROBOCLASS.CONVERTER.getlong(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, True)
            else:
                data = self.ROBOCLASS.CONVERTER.getlong(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION, False)
            self.POSITION += self.ROBOCLASS.CONVERTER.LONG_LENGTH
            return data

        elif string == 'double':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.DOUBLE_LENGTH)
            data = self.ROBOCLASS.CONVERTER.getdouble(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION)
            self.POSITION += self.ROBOCLASS.CONVERTER.DOUBLE_LENGTH
            return data

        elif string == 'float':
            self.checkbuffer(self.POSITION+self.ROBOCLASS.CONVERTER.FLOAT_LENGTH)
            data = self.ROBOCLASS.CONVERTER.getfloat(self.ROBOCLASS.NETWORK.PACKETDATA, self.POSITION)
            self.POSITION += self.ROBOCLASS.CONVERTER.FLOAT_LENGTH
            return data

        elif string == 'slot':
            self.ROBOCLASS.PACKETS.TYPES.getslot()
            return None

        elif string == 'entitymetadata':
            self.ROBOCLASS.PACKETS.TYPES.getentitymetadata()
            return None

    def initpointer(self):
        self.POSITION = 0

    def read(self, value):
        if type(value) == str:
            return self.nickparse(value)

        elif type(value) == int:
            self.checkbuffer(self.POSITION+value)
            data = self.ROBOCLASS.NETWORK.PACKETDATA[self.POSITION:self.POSITION+value]
            self.POSITION += value
            return data

        else:
            raise Exception("PacketPointer: Invalid value type for read() function")

    def getposition(self):
        return self.POSITION

class types():
    def __init__(self, roboclass):
        self.ROBOCLASS = roboclass

    def getslot(self):
        blockid = self.ROBOCLASS.PACKETS.POINTER.read('short')
        if not blockid == -1:
            self.ROBOCLASS.PACKETS.POINTER.read('byte')
            self.ROBOCLASS.PACKETS.POINTER.read('short')
            metadatalength = self.ROBOCLASS.PACKETS.POINTER.read('short')
            if not metadatalength == -1:
                self.ROBOCLASS.PACKETS.POINTER.read(metadatalength)

    def makeslot(self):
        pass

    def getentitymetadata(self):
        x = self.ROBOCLASS.PACKETS.POINTER.read('ubyte')
        while not x == 127:
            #print("Index:", x & 0x1F)
            ty = x >> 5
            if ty == 0:
                #print("Type 0")
                self.ROBOCLASS.PACKETS.POINTER.read('byte')

            if ty == 1:
                #print("Type 1")
                self.ROBOCLASS.PACKETS.POINTER.read('short')

            if ty == 2:
                #print("Type 2")
                self.ROBOCLASS.PACKETS.POINTER.read('int')

            if ty == 3:
                #print("Type 3")
                self.ROBOCLASS.PACKETS.POINTER.read('float')

            if ty == 4:
                #print("Type 4")
                self.ROBOCLASS.PACKETS.POINTER.read('string')

            if ty == 5:
                #print("Type 5")
                self.ROBOCLASS.PACKETS.POINTER.read('short')
                self.ROBOCLASS.PACKETS.POINTER.read('byte')
                self.ROBOCLASS.PACKETS.POINTER.read('short')

            if ty == 6:
                #print("Type 6")
                self.ROBOCLASS.PACKETS.POINTER.read('int')
                self.ROBOCLASS.PACKETS.POINTER.read('int')
                self.ROBOCLASS.PACKETS.POINTER.read('int')

            x = self.ROBOCLASS.PACKETS.POINTER.read('ubyte')

    def makeentitymetadata(self):
        pass

    def getchunk(self):
        pass

    def makechunk(self):
        pass
