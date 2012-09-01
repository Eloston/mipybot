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

    def initiatehandlers(self):
        exclude = ["__pycache__", "__init__.py", "template.py"]
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

    def process(self, data):
        while len(data) > 0:
            header = data[0] # Apparently this will turn that byte into an integer for me. How convenient!
            print("Got header", header, ",", hex(header))
            handclass = self.gethandler(header)
            if handclass == None:
                print("Unknown packet", hex(header))
                #print("Data:", data)
                self.ROBOCLASS.stop()
                break
            print("Received packet", handclass.NAME)
            data = data[1:] # Strip out packet header
            packetdatalength = handclass.getlength(self.ROBOCLASS, data)
            if packetdatalength > len(data):
                print("***WARNING: CALCULATED PACKET LENGTH EXCEEDS LENGTH OF UNPROCESSED DATA***")
            packetdata = data[:packetdatalength]
            data = data[packetdatalength:]
            if len(data) == 0:
                print("***INFO: Data hit length of 0")
            handclass.receive(self.ROBOCLASS, packetdata)
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
