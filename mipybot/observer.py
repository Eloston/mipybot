'''
MiPyBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MiPyBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MiPyBot.  If not, see {http://www.gnu.org/licenses/}.
'''

# An implementation of the Observer pattern
# Used in Managers

class Observable:
    def __init__(self):
        self.observers = list()

    def add_observer(self, observer_obj):
        self.observers.append(observer_obj)

    def remove_observer(self, observer_obj):
        self.observers.remove(observer_obj)

    def notify_observers(self, *args):
        for observer in self.observers:
            observer.notify(*args)

class Observer:
    def __init__(self, function=lambda: None):
        self.callback = function

    def notify(self, *args):
        self.callback(*args)
