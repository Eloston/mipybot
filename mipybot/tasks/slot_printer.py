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

import mipybot.windows
import mipybot.observer

def print_slot_info(window_obj, slot_obj_list):
    print("***WINDOW: " + str(window_obj.id))
    for slot_obj in slot_obj_list:
        if slot_obj.item is None:
            print(str(slot_obj.index) + ": " + str(slot_obj.item))
        else:
            print(str(slot_obj.index) + ": " + str(slot_obj.item.type))

def init():
    mipybot.windows.WindowManager.slot_change_observable.add_observer(mipybot.observer.Observer(print_slot_info))
