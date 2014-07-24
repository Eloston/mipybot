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

    def send_message(message_id, *args):
        mipybot.networking.desktop.Protocol.send_message(message_id, *args)

    def start(self):
        loop = asyncio.get_event_loop()
        mipybot.networking.desktop.init()
        coro = loop.create_connection(lambda: mipybot.networking.desktop.Protocol, self.host, self.port)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()

NetworkManager = None

def init(*args):
    global NetworkManager
    NetworkManager = NetworkManagerClass(*args)
