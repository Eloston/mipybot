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

import argparse
import asyncio
import mipybot.networking
import mipybot.player
import mipybot.chat
import mipybot.windows
import mipybot.tasks

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--host", help="The host's IP address or domain name to connect to", type=str, default="localhost")
    arg_parser.add_argument("--port", help="The port the server listens on", type=int, default=25565)
    arg_parser.add_argument("--host-spoof", help="Send a different host value to the server when connecting", type=str, default=None)
    arg_parser.add_argument("--port-spoof", help="Send a different port value to the server when connecting", type=int, default=None)
    arg_parser.add_argument("--playername", help="The in-game name to use", type=str, default="Player")
    arg_returns = arg_parser.parse_args()

    print("***MiPyBot INIT***")

    mipybot.networking.init(arg_returns.host, arg_returns.port, arg_returns.host_spoof, arg_returns.port_spoof)
    mipybot.player.init(arg_returns.playername)
    mipybot.windows.init()
    mipybot.chat.init()
    mipybot.tasks.init()

    loop = asyncio.get_event_loop()
    print("***MiPyBot START***")
    loop.run_forever()
    print("***MiPyBot STOP***")
    loop.close()
