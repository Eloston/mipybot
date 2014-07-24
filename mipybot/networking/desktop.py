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
import io
import struct
import json
import enum
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

import mipybot.networking
import mipybot.player

class Message:
    def __init__(self, bytesio):
        self.buffer = bytesio

    # Struct convenience methods

    def _read(self, struct_format, length):
        return struct.unpack(struct_format, self.buffer.read(length))[0]

    def _write(self, struct_format, value):
        self.buffer.write(struct.pack(struct_format, value))

    # bool

    def _read_bool(self):
        return self._read("?", 1)

    def _write_bool(self, value):
        self._write("?", value)

    # byte

    def _read_byte(self):
        return self._read("b", 1)

    def _write_byte(self, value):
        self._write("b", value)

    # ubyte

    def _read_ubyte(self):
        return self._read("B", 1)

    def _write_ubyte(self, value):
        self._write("B", value)

    # short

    def _read_short(self):
        return self._read("!h", 2)

    def _write_short(self, value):
        self._write("!h", value)

    # ushort

    def _read_ushort(self):
        return self._read("!H", 2)

    def _write_ushort(self, value):
        self._write("!H", value)

    # int

    def _read_int(self):
        return self._read("!i", 4)

    def _write_int(self, value):
        self._write("!i", value)

    # uint

    def _read_uint(self):
        return self._read("!I", 4)

    def _write_uint(self, value):
        self._write("!I", value)

    # long

    def _read_long(self):
        return self._read("!q", 8)

    def _write_long(self, value):
        self._write("!q", value)

    # ulong

    def _read_ulong(self):
        return self._read("!Q", 8)

    def _write_ulong(self, value):
        self._write("!Q", value)

    # float

    def _read_float(self):
        return self._read("!f", 4)

    def _write_float(self, value):
        self._write("!f", value)

    # double

    def _read_double(self):
        return self._read("!d", 8)

    def _write_double(self, value):
        self._write("!d", value)

    # varint

    def _read_varint(self):
        d = 0
        for i in range(5):
            b = ord(self.buffer.read(1))
            d |= (b & 0x7F) << 7*i
            if not b & 0x80:
                break
        return d

    def _write_varint(self, d):
        o = bytes()
        while True:
            b = d & 0x7F
            d >>= 7
            o += struct.pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        self.buffer.write(o)

    # string

    def _read_string(self):
        str_len = self._read_varint()
        return self.buffer.read(str_len).decode("UTF-8")

    def _write_string(self, value):
        encoded_string = value.encode("UTF-8")
        self._write_varint(len(encoded_string))
        self.buffer.write(encoded_string)

    # slot

    def _read_slot(self):
        # This is a stub
        blockid = self._read_short()
        if not blockid == -1:
            self._read_byte()
            self._read_short()
            metadatalength = self._read_short()
            if not metadatalength == -1:
                self.buffer.read(metadatalength)

    def _write_slot(self):
        raise NotImplementedError()

    # metadata

    def _read_metadata(self):
        # This is a stub
        x = self._read_ubyte()
        while not x == 127:
            ty = x >> 5
            if ty == 0:
                self._read_byte()
            if ty == 1:
                self._read_short()
            if ty == 2:
                self._read_int()
            if ty == 3:
                self._read_float()
            if ty == 4:
                self._read_string()
            if ty == 5:
                self._read_slot()
            if ty == 6:
                self._read_int()
                self._read_int()
                self._read_int()
            x = self._read_ubyte()

    def _write_metadata(self):
        raise NotImplementedError()

    def _read_json(self):
        return json.dumps(self._read_string())

    # Methods to override per-message

    def parse(self):
        raise NotImplementedError()

    def write(self, *args):
        raise NotImplementedError()

# Login and Play

class Disconnect(Message):
    def parse(self):
        print("Received disconnect: " + self._read_json()["text"])

# Handshake Messages

class Handshake(Message):
    def write(self):
        print("Send Handshake")
        self._write_varint(5) # 1.7.6 through 1.7.10
        if mipybot.networking.NetworkManager.host_spoof is None:
            self._write_string(mipybot.networking.NetworkManager.host)
        else:
            self._write_string(mipybot.networking.NetworkManager.host_spoof)
        if mipybot.networking.NetworkManager.port_spoof is None:
            self._write_ushort(mipybot.networking.NetworkManager.port)
        else:
            self._write_ushort(mipybot.networking.NetworkManager.port_spoof)
        self._write_varint(2) # Login status

# Login Messages

class EncryptionRequest(Message):
    def parse(self):
        print("Read Encryption Request")
        self._read_string() # Server ID
        encoded_public_key_len = self._read_short()
        Encryption.set_encoded_public_key(self.buffer.read(encoded_public_key_len))
        verification_token_len = self._read_short()
        Encryption.set_verification_token(self.buffer.read(verification_token_len))
        Encryption.generate_pkcscipher()
        Encryption.generate_aes()
        Protocol.send_message(0x01)

class LoginSuccess(Message):
    def parse(self):
        print("Read Login Success")
        print("UUID: " + self._read_string())
        print("Username: " + self._read_string())
        Protocol.set_current_state(NetworkState.play)
        print("Now Play state")

class LoginStart(Message):
    def write(self):
        print("Send Login Start")
        self._write_string(mipybot.player.PlayerManager.player_name)

class EncryptionResponse(Message):
    def write(self):
        print("Send Encryption Response")
        encrypted_aes_key = Encryption.pkcs_encrypt(Encryption.aes_key)
        self._write_short(len(encrypted_aes_key))
        self.buffer.write(encrypted_aes_key)
        encrypted_verification_token = Encryption.pkcs_encrypt(Encryption.verification_token)
        self._write_short(len(encrypted_verification_token))
        self.buffer.write(encrypted_verification_token)
        Encryption.enable_encryption()

class NetworkState(enum.Enum):
    handshake = 0
    login = 1
    play = 2

class DesktopProtocolClass(asyncio.Protocol):
    def __init__(self):
        self.current_state = NetworkState.handshake

        # Message delegates
        # tuple format: (message_receive_handler, message_send_handler)

        self.play_message_delegates = dict()

        self.login_message_delegates = {
            0x00: (Disconnect, LoginStart),
            0x01: (EncryptionRequest, EncryptionResponse),
            0x02: (LoginSuccess, None)
        }

        self.handshake_message_delegates = {
            0x00: (None, Handshake)
        }

    def _read_buffer(self, length, buffer=None):
        if buffer is None:
            buffer = self.databuffer
        data = b''
        while True:
            data += buffer.read(length - len(data))
            if len(data) == length:
                return data
            else:
                yield

    def _unpack_varint(self, buffer=None):
        d = 0
        for i in range(5):
            b = ord((yield from self._read_buffer(1, buffer)))
            d |= (b & 0x7F) << 7*i
            if not b & 0x80:
                break
        return d

    def _create_varint(self, d):
        o = bytes()
        while True:
            b = d & 0x7F
            d >>= 7
            o += struct.pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        return o

    def _message_delegator_generator(self):
        while True:
            message_length = yield from self._unpack_varint()
            message_data = yield from self._read_buffer(message_length)
            message_buffer = io.BytesIO(message_data)
            message_id = yield from self._unpack_varint(message_buffer)
            if self.current_state == NetworkState.play:
                self.play_message_delegates[message_id][0](message_buffer).parse()
            elif self.current_state == NetworkState.login:
                self.login_message_delegates[message_id][0](message_buffer).parse()
            elif self.current_state == NetworkState.handshake:
                self.handshake_message_delegates[message_id][0](message_buffer).parse()
            else:
                raise Exception("Invalid state" + str(self.current_state))
            remainder_data = self.databuffer.read()
            self.databuffer.close()
            del self.databuffer
            self.databuffer = io.BytesIO(remainder_data)
            del remainder_data

    # Public methods

    def set_current_state(self, newstate):
        self.current_state = newstate

    def send_message(self, message_id, *args):
        # Needs to create io.BytesIO() buffer for message to write to
        # Needs to use _create_varint() to create varint ID and message length
        # Needs to lock? (depends if transport is thread-safe)
        write_buffer = io.BytesIO()
        if self.current_state == NetworkState.play:
            self.play_message_delegates[message_id][1](write_buffer).write(*args)
        elif self.current_state == NetworkState.login:
            self.login_message_delegates[message_id][1](write_buffer).write(*args)
        elif self.current_state == NetworkState.handshake:
            self.handshake_message_delegates[message_id][1](write_buffer).write(*args)
        else:
            raise Exception("Invalid state" + str(self.current_state))
        write_buffer.seek(0)
        message_data = self._create_varint(message_id) + write_buffer.read()
        message_data = self._create_varint(len(message_data)) + message_data
        if Encryption.encryption_enabled:
            message_data = Encryption.aes_encrypt(message_data)
        self.transport.write(message_data)

    # asyncio.Protocol methods

    def connection_made(self, transport):
        self.transport = transport
        self.databuffer = io.BytesIO()
        self.delegate_instance = self._message_delegator_generator()

        self.send_message(0x00) # Handshake
        self.set_current_state(NetworkState.login)
        print("Now Login state")
        self.send_message(0x00) # Login start

    def data_received(self, data):
        current_pos = self.databuffer.tell()
        if Encryption.encryption_enabled:
            self.databuffer.write(Encryption.aes_decrypt(data))
        else:
            self.databuffer.write(data)
        self.databuffer.seek(current_pos)
        try:
            next(self.delegate_instance)
        except StopIteration:
            asyncio.get_event_loop().stop()

    def connection_lost(self, exc):
        print("Closing connection!")
        asyncio.get_event_loop().stop()

class EncryptionClass:
    def __init__(self):
        self.aes_cipher_dec = None
        self.aes_cipher_enc = None
        self.aes_key = None
        self.pkcs_cipher = None
        self.encoded_public_key = None
        self.public_key = None
        self.verification_token = None

        self.encryption_enabled = False

    def enable_encryption(self):
        self.encryption_enabled = True

    def set_verification_token(self, data):
        self.verification_token = data

    def set_encoded_public_key(self, data):
        self.encoded_public_key = data

    def generate_aes(self):
        '''
        Generates the AES key, encrypting cipher, and decrypting cipher
        '''
        self.aes_key = Crypto.Random.new().read(AES.block_size)
        self.aes_cipher_enc = AES.new(self.aes_key, AES.MODE_CFB, self.aes_key)
        self.aes_cipher_dec = AES.new(self.aes_key, AES.MODE_CFB, self.aes_key)

    def generate_pkcscipher(self):
        '''+
        Decodes a public key from the input into ASN.1 format defined by X.509, and generates a PKCS v1.5 cipher
        '''
        self.public_key = RSA.importKey(self.encoded_public_key)
        self.pkcs_cipher = PKCS1_v1_5.new(self.public_key)

    def pkcs_encrypt(self, data):
        '''
        Encrypts data with the server's public key
        '''
        return self.pkcs_cipher.encrypt(data)

    def aes_encrypt(self, data):
        '''
        Encrypts data with the symnetric key
        '''
        return self.aes_cipher_enc.encrypt(data)

    def aes_decrypt(self, data):
        '''
        Decrypts data witht he symnetric key
        '''
        return self.aes_cipher_dec.decrypt(data)

Encryption = None
Protocol = None

def init():
    global Encryption
    Encryption = EncryptionClass()
    global Protocol
    Protocol = DesktopProtocolClass()
