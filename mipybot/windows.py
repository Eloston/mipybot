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

import enum
import asyncio

import mipybot.observer
import mipybot.networking

class Slot:
    def __init__(self, item_obj, index=None):
        self.item = item_obj
        self.index = index

class Window:
    window_size = 0 # Overridden by subclasses
    class slot_ranges(enum.Enum): # Overridden by subclasses
        main_inventory = None
        hotbar = None

    def __init__(self, window_id, window_title):
        self.id = window_id
        self.slots = [None for i in range(self.window_size)]
        self.transaction_done = asyncio.Event()
        self.transaction_done.set()

    def set_slots(self, slot_dict):
        for index in slot_dict:
            self.slots[index] = slot_dict[index]

    @asyncio.coroutine
    def slot_by_index(self, index, range_type=None):
        yield from self.transaction_done.wait()
        if range_type is None:
            return self.slots[index]
        else:
            lower, upper = range_type.value
            if (index >= 0) and (lower + index <= upper):
                return self.slots[lower + index]
            else:
                raise Exception("index out of bounds: " + str(index) + " for range " + str(lower) + ", " + str(upper))

    @asyncio.coroutine
    def slots_by_range(self, range_type):
        yield from self.transaction_done.wait()
        lower_index, upper_index = range_type
        return self.slots[lower_index:upper_index+1]

    def _slot_by_coordinate(self, row, col, row_count, col_count, range_type):
        # (0, 0) at upper left slot
        if not (row >= 0) and (row <= row_count-1):
            raise Exception("row index out of bounds: " + str(row))
        if not (col >= 0) and (col <= col_count-1):
            raise Exception("col index out of bounds: " + str(col))
        slot_index = row*(col_count-1) + col
        slot_index += range_type[0]
        return self.slots[slot_index]

    @asyncio.coroutine
    def main_inventory_slot_by_coordinate(self, row, col):
        yield from self.transaction_done.wait()
        return self._slot_by_coordinate(row, col, 3, 9, self.slot_ranges.main_inventory)

    @asyncio.coroutine
    def slot_action(self, action_type, slot_obj=None):
        yield from self.transaction_done.wait()
        self.transaction_done.clear()
        mode, button, slot_type = action_type.value
        if slot_type is -999:
            WindowManager.send_transaction(self, Slot(None, -999), mode, button)
        else:
            WindowManager.send_transaction(self, slot_obj, mode, button)

class InventoryWindow(Window):
    window_size = 45
    class slot_ranges(enum.Enum):
        crafting_output = (0, 0)
        crafting_input = (1, 4)
        armor = (5, 8)
        main_inventory = (9, 35)
        hotbar = (36, 44)

class CraftingWindow(Window):
    pass

class ChestWindow(Window):
    def __init__(self, *args):
        super().__init__(*args)
        self.is_large = None

class FurnaceWindow(Window):
    pass

class DispenserWindow(Window):
    pass

class EnchantmentTableWindow(Window):
    pass

WindowTypes = {
    0: ChestWindow,
    1: CraftingWindow,
    2: FurnaceWindow,
    3: DispenserWindow,
    4: EnchantmentTableWindow,
    5: None,
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: None
}

class WindowActions(enum.Enum):
    # (mode, button, slot_type: None or -999)
    left_mouse_click = (0, 0, None)
    right_mouse_click = (0, 1, None)
    drop_item = (4, 0, None)
    drop_stack = (4, 1, None)

class WindowManagerClass:
    def __init__(self):
        self.windows = dict() # (Window ID): (Window Object)
        self.windows[0] = InventoryWindow(0, "Inventory")
        self._action_count = 1
        self.open_observable = mipybot.observer.Observable()
        self.close_observable = mipybot.observer.Observable()
        self.property_change_observable = mipybot.observer.Observable()
        self.slot_change_observable = mipybot.observer.Observable()

    def get_inventory(self):
        return self.windows[0]

    def open(self, window_obj):
        # Run by NetworkManager
        self.windows[window_obj.id] = window_obj
        self.open_observable.notify_observers(window_obj)

    def close(self, window_obj, voluntary=True):
        # voluntary == False if run by NetworkManager
        if voluntary:
            mipybot.networking.NetworkManager.send_message(window_obj)
        del self.windows[window_obj.id]
        self.close_observable.notify_observers(window_obj)

    def set_slots(self, window_id, slot_dict):
        # Run by NetworkManager
        self.windows[window_id].set_slots(slot_dict)
        self.slot_change_observable.notify_observers(self.windows[window_id], [i for i in slot_dict.values()])

    def send_transaction(self, window_obj, slot_obj, mode, button):
        # Run by Window objects
        if self._action_count >= 32767:
            self._action_count = 1
        mipybot.networking.NetworkManager.send_message(0x0E, self._action_count, window_obj, slot_obj, mode, button)
        self._action_count += 1

    def confirm_transaction(self, window_id, accepted):
        # Run by NetworkManager
        window_obj = self.windows[window_id]
        window_obj.transaction_done.set()

WindowManager = None

def init(*args):
    global WindowManager
    WindowManager = WindowManagerClass(*args)
