import os
import os.path
import sys
import struct
'''
Format for the protocol dictionary:
{ProtocolVer: ProtocolObject}
Where ProtocolVer is the Minecraft Protocol verison, (such as 39 for Minecraft 1.3), and ProtocolObject is the packet protocol object.

Format for the protocol version dictionary:
{ProtocolVerNum: ProtcolVerString}
Where ProtcolVerNum is the numeric version (such as 39 for Minecraft 1.3) and ProtcolVerString is a string for the Minecraft version(s) (such as 1.3 - current)
'''
class protocolmanager():
    def __init__(self):
        self.PROTOCOLDICT = dict()

    def initiateprotocols(self):
        '''
        Scans and imports protocol directories.
        It will modify PROTOCOLDICT into the format:
        {NumericProtocolVersion: ProtocolObject, ...}
        '''
        exclude = ["__pycache__", "__init__.py"]
        listing = os.listdir(os.path.dirname(__file__))
        for item in listing:
            if item in exclude:
                continue

            elif os.path.isfile(os.path.join(os.path.dirname(__file__), item)):
                continue

            elif os.path.isdir(os.path.join(os.path.dirname(__file__), item)):
                if '.' in item:
                    continue
                try:
                    tempcol = __import__(item, globals=globals(), locals=locals())
                    tempver = tempcol.PROTOCOLVERSION[0]
                    self.PROTOCOLDICT[tempver] = tempcol
                except:
                    pass

    def getprotocolverdict(self):
        '''
        Returns a dictionary in the format:
        {NumericProtocolVersion: MinecraftVersions, ...}
        '''
        protocolvernumlist = list(self.PROTOCOLDICT.keys())
        tempdict = dict()
        for vernum in protocolvernumlist:
            tempdict[vernum] = self.PROTOCOLDICT[vernum].PROTOCOLVERSION[1]
        return tempdict

    def getprotocolobject(self, protocolver):
        '''
        Returns the specified protocol version, or None if it is not found
        '''
        try:
            roboclassbase = self.PROTOCOLDICT[protocolver]
        except:
            roboclassbase = None
        return roboclassbase
