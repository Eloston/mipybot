import threading
import logging
import sys

# Signaling definitions

class signalmanager():
    def __init__(self):
        self.SIGNALS = {}
        self.EMITTINGTHREADS = set()

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

    def emit(self, signame, separateThread=False):
        emittingsignal = self.SIGNALS[signame]
        if separateThread:
            emitthread = threading.Thread(target=emittingsignal.emit)
            emitthread.start()
            self.EMITTINGTHREADS.add(emitthread)
            self.cleardeadthreads()
        else:
            emittingsignal.emit()

    def cleardeadthreads(self):
        while True:
            asignal = self.EMITTINGTHREADS.pop()
            if asignal.is_alive():
                self.EMITTINGTHREADS.add(asignal)
                del asignal
            else:
                del asignal
                break

class signal():
    def __init__(self, name):
        self.NAME = name
        self.RECEIVERS = []

    def addreceiver(self, receiver, keywordargs=dict()):
        self.RECEIVERS.append([receiver, keywordargs])

    def delreceiver(self, receiver, keywordargs=dict()):
        for receiverlist in self.RECEIVERS:
            if receiverlist[0] == receiver and receiverlist[1] == keywordargs:
                self.RECEIVERS.remove(receiverlist)
                break

    def emit(self):
        for receiverlist in self.RECEIVERS:
            receiverlist[0](**receiverlist[1])

class loggingtools():
    def __init__(self):
        self.LOGGINGHANDLER = logging.StreamHandler(sys.stdout)
        self.LOGGINGHANDLER.setFormatter(logging.Formatter('%(name)s|%(levelname)s - %(message)s'))

    def makelogger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.LOGGINGHANDLER)
        return logger
