import yapsy.PluginManager
import yapsy.PluginFileLocator
import sys
import yapsy
import inspect
import os.path
import logging
yapsy.log.setLevel(logging.DEBUG)
yapsy.log.addHandler(logging.StreamHandler(sys.stdout))

import constants

class manager:
    def __init__(self, roboclass):
        self.BASEDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.PLUGINMANAGER = yapsy.PluginManager.PluginManager(directories_list=[os.path.join(self.BASEDIR, 'plugins')], plugin_info_ext='mipybot-plugin')
        self.ROBOCLASS = roboclass
        self.VALIDPLUGINS = list()

    def initPlugins(self):
        self.PLUGINMANAGER.collectPlugins()
        robotAPIversion = constants.APIversion
        for pluginInfo in self.PLUGINMANAGER.getAllPlugins():
            pluginAPIversion = pluginInfo.plugin_object.getPluginAPIversion()
            if robotAPIversion == pluginAPIversion:
                pluginInfo.plugin_object.setRoboclass(self.ROBOCLASS)
                self.VALIDPLUGINS.append(pluginInfo.name)

    def startPlugins(self):
        for pluginName in self.VALIDPLUGINS:
            self.PLUGINMANAGER.activatePluginByName(pluginName)

    def stopPlugins(self):
        for pluginName in self.VALIDPLUGINS:
            self.PLUGINMANAGER.deactivatePluginByName(pluginName)
