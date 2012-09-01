from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Plugin Message"
        self.HEADER = 0xFA

    def receive(self, roboclass, data):
        channel = roboclass.CONVERTER.getstringdata(data)['string']
        print("Plugin channel:", channel)

    def getlength(self, roboclass, data):
        Length = roboclass.CONVERTER.getstringdata(data)['length']
        Length += roboclass.CONVERTER.SHORT_LENGTH
        Length += roboclass.CONVERTER.getshort(data, Length)
        Length += roboclass.CONVERTER.SHORT_LENGTH
        return Length
