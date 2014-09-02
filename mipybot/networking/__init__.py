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
import mipybot.networking.desktop

class NetworkManagerClass:
    def __init__(self, host, port, host_spoof, port_spoof):
        self.host = host
        self.port = port
        self.host_spoof = host_spoof
        self.port_spoof = port_spoof

        self.event_loop = asyncio.get_event_loop()
        mipybot.networking.desktop.init()
        coro = self.event_loop.create_connection(lambda: mipybot.networking.desktop.Protocol, self.host, self.port)
        self.event_loop.create_task(coro)

    def send_message(self, message_id, *args):
        # TODO: Decide which send_message to use depending whether this is the desktop or pocket protocol
        self.event_loop.call_soon_threadsafe(mipybot.networking.desktop.Protocol.send_message, message_id, *args)

NetworkManager = None

def init(*args):
    global NetworkManager
    NetworkManager = NetworkManagerClass(*args)
