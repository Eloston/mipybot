import os
import os.path
import sys
import struct
protocoldict = dict()
'''
Format for the protocol dictionary:
{ProtocolVer: ProtocolObject}
Where ProtocolVer is the Minecraft Protocol verison, (such as 39 for Minecraft 1.3), and ProtocolObject is the packet protocol object.

Format for the protocol version dictionary:
{ProtocolVerNum: ProtcolVerString}
Where ProtcolVerNum is the numeric version (such as 39 for Minecraft 1.3) and ProtcolVerString is a string for the Minecraft version(s) (such as 1.3 - current)
'''

def initiateprotocols():
    exclude = ["__pycache__", "__init__.py"]
    listing = os.listdir(os.path.dirname(__file__))
    global protocoldict
    for item in listing:
        if item in exclude:
            continue

        elif os.path.isfile(item):
            continue

        elif os.path.isdir(item):
            if '.' in item:
                continue
        else:
            try:
                tempcol = __import__(item, globals=globals(), locals=locals())
                tempver = tempcol.PROTOCOLVERSION[0]
                protocoldict[tempver] = tempcol
            except:
                pass

def getprotocol(protocolver):
    global protocoldict
    try:
        protocol = protocoldict[protocolver]
    except:
        protocol = None
    return protocol

def getprotocolverdict():
    global protocoldict
    protocolvernumlist = list(protocoldict.keys())
    tempdict = dict()
    for vernum in protocolvernumlist:
        tempdict[vernum] = protocoldict[vernum].PROTOCOLVERSION[1]
    return tempdict

def getprotocolobject(protocolver):
    global protocoldict
    try:
        roboclassbase = protocoldict[protocolver]
    except:
        roboclassbase = None
    return roboclassbase
