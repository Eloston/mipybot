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

import mipybot.observer
import mipybot.networking

class ChatManagerClass:
    def __init__(self):
        self.new_chat_observer = mipybot.observer.Observable()

    def process_chat(self, message):
        print("Chat Message Received: " + message)
        self.new_chat_observer.notify_observers(message)

    def send_chat_message(self, message):
        # TODO: Split long messages into multiple chat messages
        mipybot.networking.NetworkManager.send_message(0x01, message)

ChatManager = None

def init(*args):
    global ChatManager
    ChatManager = ChatManagerClass(*args)
