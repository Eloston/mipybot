import imp
import sys
import os.path
from functools import wraps

class PluginError(Exception):
    def __init__(self, plugin_name, message):
        self.plugin_name = plugin_name
        self.message = message
    
    def __str__(self):
        return self.message


def find_plugins(app, search_path=''):
    enabled_plugins = set()
    found_plugins = set()
    
    for plugin in getattr(app, 'plugins', list()):
        enabled_plugins.add(plugin)
    
    plugin_searchpath = os.path.abspath(getattr(app, 'plugin_searchpath', search_path))
    for path in (os.path.join(plugin_searchpath, filename) for filename in os.listdir(plugin_searchpath)):
        if os.path.isdir(path):
            head, name = os.path.split(path)
        else:
            root, ext = os.path.splitext(path)
            if not ext == '.py':
                continue            
            head, name = os.path.split(root)
        
        if not name in enabled_plugins|found_plugins:
            found_plugins.add(name)
            
            try:
                fpd = imp.find_module(name, [head])
            except ImportError:
                continue
            else:
                yield Plugin(app, name, head, fpd) 


class PluginManager(object):
    def __init__(self, app, reserved_plugins=None):
        self.app = app
        self.plugins = dict()
        self.active_plugins = dict()
        
        self.reserved_plugins = set([] if reserved_plugins is None else reserved_plugins)
        
        self.cur_plugin = None

    def collect_plugins(self):
        plugins = find_plugins(self.app)

        for plugin in plugins:
            if plugin.name.lower() in self.reserved_plugins:
                raise PluginError(plugin.name, '"{0}" is a reserved plugin-name'.format(plugin.name))
            else:
                self.plugins[plugin.name] = plugin
    
    def load_plugins(self, plugins=None):
        for plugin in (self.plugins if plugins is None else plugins):
            self.load_plugin(plugin)
    
    def load_plugin(self, name):
        if name in self.plugins:
            self.cur_plugin = name
            #sys.path.insert(0, os.path.abspath(self.app.plugin_searchpath))
            self.plugins[name].load()
            self.plugins[name].setup()
            self.active_plugins[name] = self.plugins[name]
            #sys.path.pop(0)
            self.cur_plugin = None
        else:
            raise PluginError(name, 'Plugin "{0}" does not exist'.format(name))
    
    def reload_plugins(self, plugins=None):
        for plugin in (self.active_plugins if plugins is None else plugins):
            self.reload_plugin(plugin)
            
    def reload_plugin(self, name):
        if name in self.active_plugins:
            self.unload_plugin(name)
            #self.plugins[name].reload()
            self.load_plugin(name)
        else:
            raise PluginError(name, 'Plugin "{0}" does not exist or is not loaded'.format(name))

    def unload_plugins(self, plugins=None):
        for plugin in (self.active_plugins if plugins is None else plugins):
            self.unload_plugin(plugin)
        
    def unload_plugin(self, name):
        if name in self.active_plugins:
            self.active_plugins[name].unload()
            del self.active_plugins[name]
        else:
            raise PluginError(name, 'Plugin "{0}" does not exist or is not loaded'.format(name))


class Plugin(object):
    '''Wraps a plugin module.'''
    
    def __init__(self, app, name, path, fpd): # fpd = 3-tuple returned by imp.find_module
        self.app = app
        self.name = name
        self.path = path
        self.fpd = fpd
        self._module = None
    
    @property
    def module(self):
        if self._module is None:
            imp.acquire_lock()
            try:
                self._module = imp.load_module(self.name, *self.fpd)
            finally:
                imp.release_lock()
                if not self.fpd[0] is None:
                    self.fpd[0].close()
        
        return self._module
    
    def load(self):
        self.module
        
    def unload(self):
        self.fpd = imp.find_module(self.name, [self.path])
        self._module = None
    
    def reload(self):
        self.unload()
        self.load()
        
    def setup(self):
        self.module.setup(self.app, self)

    