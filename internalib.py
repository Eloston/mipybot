import logging
import sys
import queue
import collections

# Signaling definitions

class signalmanager():
    def __init__(self):
        self.SIGNALS = dict()

    def getsignal(self, signame):
        return self.SIGNALS[signame]

    def newsignal(self, signame):
        tmpsignal = signal(signame)
        self.addsignal(tmpsignal)

    def addsignal(self, signal):
        if not signal.NAME in iter(self.SIGNALS.keys()):
            self.SIGNALS[signal.NAME] = signal

    def delsignal(self, signame):
        del self.SIGNALS[signame]

    def emit(self, signame):
        emittingsignal = self.SIGNALS[signame]
        emittingsignal.emit()

class signal():
    def __init__(self, name):
        self.NAME = name
        self.RECEIVERS = []
        self.RECEIVER_PROCESSING = queue.Queue()
        self.ISLOCKED = False

    def flushqueue(self):
        while not self.RECEIVER_PROCESSING.empty():
            actionlist = self.RECEIVER_PROCESSING.get()
            if actionlist[0] == 'add':
                self.addreceiver(actionlist[1], actionlist[2])
            elif actionlist[0] == 'del':
                self.delreceiver(actionlist[1], actionlist[2])

    def addreceiver(self, receiver, keywordargs=dict()):
        if self.ISLOCKED:
            self.RECEIVER_PROCESSING.put(['add', receiver, keywordargs])
        else:
            self.RECEIVERS.append([receiver, keywordargs])

    def delreceiver(self, receiver, keywordargs=dict()):
        if self.ISLOCKED:
            self.RECEIVER_PROCESSING.put(['del', receiver, keywordargs])
        else:
            self.ISLOCKED = True
            for receiverlist in self.RECEIVERS:
                if receiverlist[0] == receiver and receiverlist[1] == keywordargs:
                    self.RECEIVERS.remove(receiverlist)
                    break
            self.ISLOCKED = False
            self.flushqueue()

    def emit(self):
        if not self.ISLOCKED:
            self.ISLOCKED = True
            for receiverlist in self.RECEIVERS:
                receiverlist[0](**receiverlist[1])
            self.ISLOCKED = False
            self.flushqueue()

class loggingtools():
    def __init__(self):
        self.LOGGINGHANDLER = logging.StreamHandler(sys.stdout)
        self.LOGGINGHANDLER.setFormatter(logging.Formatter('%(name)s|%(levelname)s - %(message)s'))

    def makelogger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.LOGGINGHANDLER)
        return logger
