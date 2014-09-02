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

import asyncio

import mipybot.windows
import mipybot.observer

def spew_items(window_obj, slot_obj_list):
    if isinstance(window_obj, mipybot.windows.InventoryWindow):
        for slot_obj in slot_obj_list:
            if not (slot_obj.item is None):
                asyncio.get_event_loop().create_task(window_obj.slot_action(mipybot.windows.WindowActions.drop_stack, slot_obj))
                print("Dropping " + str(slot_obj.item.type))

def init():
    mipybot.windows.WindowManager.slot_change_observable.add_observer(mipybot.observer.Observer(spew_items))
