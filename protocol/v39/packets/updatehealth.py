from . import template

class handler(template.handler):
    def __init__(self, *args):
        self.NAME = "Update Health"
        self.HEADER = 0x08

    def receive(self, roboclass, data):
        Position = 0
        hp = roboclass.CONVERTER.getshort(data, Position)
        Position += roboclass.CONVERTER.SHORT_LENGTH
        food = roboclass.CONVERTER.getshort(data, Position)
        Position += roboclass.CONVERTER.SHORT_LENGTH
        foodsaturation = roboclass.CONVERTER.getfloat(data, Position)
        healthdict = dict()
        healthdict['hp'] = hp
        healthdict['food'] = food
        healthdict['foodsaturation'] = foodsaturation
        roboclass.CHARACTER.updatehealth(healthdict)
        print("Health stats:\nHP:", hp, "\nFood:", food, "\nFood Saturation", foodsaturation)

    def getlength(self, roboclass, data):
        return roboclass.CONVERTER.SHORT_LENGTH*2+roboclass.CONVERTER.FLOAT_LENGTH
