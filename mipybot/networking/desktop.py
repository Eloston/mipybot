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
import uuid
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

import mipybot.networking
import mipybot.player

class Message:
    def __init__(self, bytesio):
        self.buffer = bytesio

    # Struct convenience methods

    def _struct_read(self, struct_format, length):
        return struct.unpack(struct_format, self.buffer.read(length))[0]

    def _struct_write(self, struct_format, value):
        self.buffer.write(struct.pack(struct_format, value))

    # bool

    def _read_bool(self):
        return self._struct_read("?", 1)

    def _write_bool(self, value):
        self._struct_write("?", value)

    # byte

    def _read_byte(self):
        return self._struct_read("b", 1)

    def _write_byte(self, value):
        self._struct_write("b", value)

    # ubyte

    def _read_ubyte(self):
        return self._struct_read("B", 1)

    def _write_ubyte(self, value):
        self._struct_write("B", value)

    # short

    def _read_short(self):
        return self._struct_read("!h", 2)

    def _write_short(self, value):
        self._struct_write("!h", value)

    # ushort

    def _read_ushort(self):
        return self._struct_read("!H", 2)

    def _write_ushort(self, value):
        self._struct_write("!H", value)

    # int

    def _read_int(self):
        return self._struct_read("!i", 4)

    def _write_int(self, value):
        self._struct_write("!i", value)

    # uint

    def _read_uint(self):
        return self._struct_read("!I", 4)

    def _write_uint(self, value):
        self._struct_write("!I", value)

    # long

    def _read_long(self):
        return self._struct_read("!q", 8)

    def _write_long(self, value):
        self._struct_write("!q", value)

    # ulong

    def _read_ulong(self):
        return self._struct_read("!Q", 8)

    def _write_ulong(self, value):
        self._struct_write("!Q", value)

    # float

    def _read_float(self):
        return self._struct_read("!f", 4)

    def _write_float(self, value):
        self._struct_write("!f", value)

    # double

    def _read_double(self):
        return self._struct_read("!d", 8)

    def _write_double(self, value):
        self._struct_write("!d", value)

    # 128-bit integer

    def _read_128int(self):
        return uuid.UUID(bytes=self.buffer.read(16)).int

    def _write_128int(self, value):
        self.buffer.write(uuid.UUID(int=value).bytes)

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
        print("Received disconnect: " + self._read_json())

# Handshake Messages

class Handshake(Message):
    def write(self):
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
        print("UUID: " + self._read_string())
        print("Username: " + self._read_string())
        Protocol.set_current_state(NetworkState.play)

class LoginStart(Message):
    def write(self):
        self._write_string(mipybot.player.PlayerManager.player_name)

class EncryptionResponse(Message):
    def write(self):
        encrypted_aes_key = Encryption.pkcs_encrypt(Encryption.aes_key)
        self._write_short(len(encrypted_aes_key))
        self.buffer.write(encrypted_aes_key)
        encrypted_verification_token = Encryption.pkcs_encrypt(Encryption.verification_token)
        self._write_short(len(encrypted_verification_token))
        self.buffer.write(encrypted_verification_token)
        Encryption.enable_encryption()

# Play Messages

class KeepAlive(Message):
    def parse(self):
        Protocol.send_message(0x00, self._read_int())

    def write(self, keep_alive_id):
        self._write_int(keep_alive_id)

class JoinGame(Message):
    def parse(self):
        self._read_int() # Player Entity ID
        self._read_ubyte() # Gamemode
        self._read_byte() # Dimension
        self._read_ubyte() # Difficulty
        self._read_ubyte() # Max players, for drawing player list
        self._read_string() # Level type

class ChatMessage(Message):
    def parse(self):
        print("Chat: " + self._read_json())

    def write(self, message):
        self._write_string(message)

class TimeUpdate(Message):
    def parse(self):
        self._read_long() # Age of the world
        self._read_long() # Time of the day

class EntityEquipment(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_short() # Equipment slot ID
        self._read_slot() # Equipment item

class SpawnPosition(Message):
    def parse(self):
        self._read_int() # Spawn x
        self._read_int() # Spawn y
        self._read_int() # Spawn z

class UpdateHealth(Message):
    def parse(self):
        self._read_float() # Health
        self._read_short() # Food
        self._read_float() # Food saturation

class Respawn(Message):
    def parse(self):
        self._read_int() # Dimension
        self._read_ubyte() # Difficulty
        self._read_ubyte() # Gamemode
        self._read_string() # Level type

class PlayerPositionAndLook(Message):
    def parse(self):
        self._read_double() # Absolute X
        self._read_double() # Absolute Y of player eyes
        self._read_double() # Absolute Z
        self._read_float() # Yaw in degrees
        self._read_float() # Pitch in degrees
        self._read_bool() # On Ground

    def write(self):
        raise NotImplementedError()

class HeldItemChange(Message):
    def parse(self):
        self._read_byte() # Selected slot index

    def write(self):
        raise NotImplementedError()

class UseBed(Message):
    def parse(self):
        self._read_int() # Player entity ID
        self._read_int() # Bed head-board X
        self._read_ubyte() # Bed head-board Y
        self._read_int() # Bed head-board Z

class Animation(Message):
    def parse(self):
        self._read_varint() # Player entity ID
        self._read_ubyte() # Animation ID

    def write(self):
        raise NotImplementedError()

class SpawnPlayer(Message):
    def parse(self):
        self._read_varint() # Player entity ID
        self._read_string() # Player UUID
        self._read_string() # Player name
        data_count = self._read_varint()
        for i in range(data_count):
            self._read_string() # Name of property
            self._read_string() # Value of property
            self._read_string() # Signature of property
        self._read_int() # Player X as fixed-point number
        self._read_int() # Player Y as fixed-point number
        self._read_int() # Player Z as fixed-point number
        self._read_byte() # Player Yaw
        self._read_byte() # Player pitch
        self._read_short() # Current holding item
        self._read_metadata()

class CollectItem(Message):
    def parse(self):
        self._read_int() # Collected entity ID
        self._read_int() # Collector entity ID

class SpawnObject(Message):
    def parse(self):
        self._read_varint() # Entity ID
        self._read_byte() # Type of object
        self._read_int() # X as fixed-point number
        self._read_int() # Y as fixed-point number
        self._read_int() # Z as fixed-point number
        self._read_byte() # Pitch
        self._read_byte() # Yaw
        object_type = self._read_int()
        if object_type > 0:
            self._read_short() # Speed X
            self._read_short() # Speed Y
            self._read_short() # Speed Z

class SpawnMob(Message):
    def parse(self):
        self._read_varint() # Entity ID
        self._read_ubyte() # Type of mob
        self._read_int() # X as fixed-point number
        self._read_int() # Y as fixed-point number
        self._read_int() # Z as fixed-point number
        self._read_byte() # Yaw
        self._read_byte() # Pitch
        self._read_byte() # Head Pitch
        self._read_short() # Velocity X
        self._read_short() # Velocity Y
        self._read_short() # Velocity Z
        self._read_metadata()

class SpawnPainting(Message):
    def parse(self):
        self._read_varint() # Entity ID
        self._read_string() # Name of painting
        self._read_int() # Center X
        self._read_int() # Center Y
        self._read_int() # Center Z
        self._read_int() # Direction

class SpawnExperienceOrb(Message):
    def parse(self):
        self._read_varint() # Entity ID
        self._read_int() # X as fixed-point number
        self._read_int() # Y as fixed-point number
        self._read_int() # Z as fixed-point number
        self._read_short() # Count

class EntityVelocity(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_short() # Velocity X
        self._read_short() # Velocity Y
        self._read_short() # Velocity Z

class DestroyEntities(Message):
    def parse(self):
        entity_count = self._read_byte()
        for i in range(entity_count):
            self._read_int() # Entity ID

class Entity(Message):
    def parse(self):
        self._read_int() # Entity ID

class EntityRelativeMove(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # delta X as fixed-point number
        self._read_byte() # delta Y as fixed-point number
        self._read_byte() # delta Z as fixed-point number

class EntityLook(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # Yaw fraction
        self._read_byte() # Pitch fraction

class EntityLookAndRelativeMove(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # delta X as fixed-point number
        self._read_byte() # delta Y as fixed-point number
        self._read_byte() # delta Z as fixed-point number
        self._read_byte() # Yaw fraction
        self._read_byte() # Pitch fraction

class EntityTeleport(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_int() # X as fixed-point number
        self._read_int() # Y as fixed-point number
        self._read_int() # Z as fixed-point number
        self._read_byte() # Yaw fraction
        self._read_byte() # Pitch fraction

class EntityHeadLook(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # Yaw

class EntityStatus(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # Entity status

class AttachEntity(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_int() # Vehicle Entity ID
        self._read_bool() # Whether to leash entity to vehicle

class EntityMetadata(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_metadata()

class EntityEffect(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # Effect ID
        self._read_byte() # Amplifier
        self._read_short() # Duration

class RemoveEntityEffect(Message):
    def parse(self):
        self._read_int() # Entity ID
        self._read_byte() # Effect ID

class SetExperience(Message):
    def parse(self):
        self._read_float() # Experience bar
        self._read_short() # Level
        self._read_short() # Total experience

class EntityProperties(Message):
    def parse(self):
        self._read_int() # Entity ID
        property_count = self._read_int()
        for i in range(property_count):
            self._read_string() # Key
            self._read_double() # Value
            modifier_count = self._read_short()
            for j in range(modifier_count):
                self._read_128int() # UUID
                self._read_double() # Amount
                self._read_byte() # Operation

class ChunkData(Message):
    def parse(self):
        self._read_int() # Chunk X coordinate
        self._read_int() # Chunk Z coordinate
        self._read_bool() # Ground-up continuous
        self._read_ushort() # Primary bit map
        self._read_ushort() # Add bit map
        chunk_data_length = self._read_int()
        self.buffer.read(chunk_data_length)

class MultiBlockChange(Message):
    def parse(self):
        self._read_int() # Chunk X coordinate
        self._read_int() # Chunk Z coordinate
        self._read_short() # number of blocks affected
        record_size = self._read_int()
        self.buffer.read(record_size)

class BlockChange(Message):
    def parse(self):
        self._read_int() # Block X coordinate
        self._read_ubyte() # Block Y coordinate
        self._read_int() # Block Z coordinate
        self._read_varint() # Block ID
        self._read_ubyte() # Block metadata

class BlockAction(Message):
    def parse(self):
        self._read_int() # Block X
        self._read_short() # Block Y
        self._read_int() # block Z
        self._read_ubyte()
        self._read_ubyte()
        self._read_varint()

class BlockBreakAnimation(Message):
    def parse(self):
        self._read_varint()
        self._read_int()
        self._read_int()
        self._read_int()
        self._read_byte()

class MapChunkBulk(Message):
    def parse(self):
        chunk_count = self._read_short()
        data_length = self._read_int()
        self._read_bool()
        self.buffer.read(data_length)
        for i in range(chunk_count):
            self._read_int()
            self._read_int()
            self._read_ushort()
            self._read_ushort()

class Explosion(Message):
    def parse(self):
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_float()
        record_count = self._read_int()
        for i in range(record_count):
            self._read_byte()
            self._read_byte()
            self._read_byte()
        self._read_float()
        self._read_float()
        self._read_float()

class Effect(Message):
    def parse(self):
        self._read_int()
        self._read_int()
        self._read_byte()
        self._read_int()
        self._read_int()
        self._read_bool()

class SoundEffect(Message):
    def parse(self):
        self._read_string()
        self._read_int()
        self._read_int()
        self._read_int()
        self._read_float()
        self._read_ubyte()

class Particle(Message):
    def parse(self):
        self._read_string()
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_float()
        self._read_int()

class ChangeGameState(Message):
    def parse(self):
        self._read_ubyte()
        self._read_float()

class SpawnGlobalEntity(Message):
    def parse(self):
        self._read_varint()
        self._read_byte()
        self._read_int()
        self._read_int()
        self._read_int()

class OpenWindow(Message):
    def parse(self):
        self._read_ubyte()
        self._read_ubyte()
        self._read_string()
        self._read_ubyte()
        self._read_bool()
        self._read_int()

class CloseWindow(Message):
    def parse(self):
        self._read_ubyte()

    def write(self):
        raise NotImplementedError()

class SetSlot(Message):
    def parse(self):
        self._read_byte()
        self._read_short()
        self._read_slot()

class WindowItems(Message):
    def parse(self):
        self._read_ubyte()
        slot_count = self._read_short()
        for i in range(slot_count):
            self._read_slot()

class WindowProperty(Message):
    def parse(self):
        self._read_ubyte()
        self._read_short()
        self._read_short()

class ConfirmTransaction(Message):
    def parse(self):
        self._read_ubyte()
        self._read_short()
        self._read_bool()

    def write(self):
        raise NotImplementedError()

class UpdateSign(Message):
    def parse(self):
        self._read_int()
        self._read_short()
        self._read_int()
        self._read_string()
        self._read_string()
        self._read_string()
        self._read_string()

    def write(self):
        raise NotImplementedError()

class Maps(Message):
    def parse(self):
        self._read_varint()
        data_length = self._read_short()
        self.buffer.read(data_length)

class UpdateBlockEntity(Message):
    def parse(self):
        self._read_int()
        self._read_short()
        self._read_int()
        self._read_ubyte()
        data_length = self._read_short()
        self.buffer.read(data_length)

class SignEditorOpen(Message):
    def parse(self):
        self._read_int()
        self._read_int()
        self._read_int()

class Statistics(Message):
    def parse(self):
        entry_count = self._read_varint()
        for i in range(entry_count):
            self._read_string()
            self._read_varint()

class PlayerListItem(Message):
    def parse(self):
        self._read_string()
        self._read_bool()
        self._read_short()

class PlayerAbilities(Message):
    def parse(self):
        self._read_byte()
        self._read_float()
        self._read_float()

    def write(self):
        raise NotImplementedError()

class TabComplete(Message):
    def parse(self):
        count = self._read_varint()
        for i in range(count):
            self._read_string()

    def write(self):
        raise NotImplementedError()

class ScoreboardObjective(Message):
    def parse(self):
        self._read_string()
        self._read_string()
        self._read_byte()

class UpdateScore(Message):
    def parse(self):
        self._read_string()
        self._read_byte()
        self._read_string()
        self._read_int()

class DisplayScoreboard(Message):
    def parse(self):
        self._read_byte()
        self._read_string()

class Teams(Message):
    def parse(self):
        self._read_string()
        mode = self._read_byte()
        if (mode is 0) or (mode is 2):
            self._read_string()
            self._read_string()
            self._read_string()
            self._read_byte()
        if (mode is 0) or (mode is 3) or (mode is 4):
            player_count = self._read_short()
            for i in range(player_count):
                self._read_string()

class PluginMessage(Message):
    def parse(self):
        self._read_string()
        data_length = self._read_short()
        self.buffer.read(data_length)

    def write(self):
        raise NotImplementedError()

class UseEntity(Message):
    def write(self):
        raise NotImplementedError()

class Player(Message):
    def write(self):
        raise NotImplementedError()

class PlayerPosition(Message):
    def write(self):
        raise NotImplementedError()

class PlayerLook(Message):
    def write(self):
        raise NotImplementedError()

class PlayerDigging(Message):
    def write(self):
        raise NotImplementedError()

class PlayerBlockPlacement(Message):
    def write(self):
        raise NotImplementedError()

class EntityAction(Message):
    def write(self):
        raise NotImplementedError()

class SteerVehicle(Message):
    def write(self):
        raise NotImplementedError()

class ClickWindow(Message):
    def write(self):
        raise NotImplementedError()

class CreativeInventoryAction(Message):
    def write(self):
        raise NotImplementedError()

class EnchantItem(Message):
    def write(self):
        raise NotImplementedError()

class ClientSettings(Message):
    def write(self):
        raise NotImplementedError()

class ClientStatus(Message):
    def write(self):
        raise NotImplementedError()

class NetworkState(enum.Enum):
    handshake = 0
    login = 1
    play = 2

class DesktopProtocolClass(asyncio.Protocol):
    def __init__(self):
        self.current_state = NetworkState.handshake

        # Message delegates
        # Tuple format: (message_receive_handler, message_send_handler)

        self.play_message_delegates = {
            0x00: (KeepAlive, KeepAlive),
            0x01: (JoinGame, ChatMessage),
            0x02: (ChatMessage, UseEntity),
            0x03: (TimeUpdate, Player),
            0x04: (EntityEquipment, PlayerPosition),
            0x05: (SpawnPosition, PlayerLook),
            0x06: (UpdateHealth, PlayerPositionAndLook),
            0x07: (Respawn, PlayerDigging),
            0x08: (PlayerPositionAndLook, PlayerBlockPlacement),
            0x09: (HeldItemChange, HeldItemChange),
            0x0A: (UseBed, Animation),
            0x0B: (Animation, EntityAction),
            0x0C: (SpawnPlayer, SteerVehicle),
            0x0D: (CollectItem, CloseWindow),
            0x0E: (SpawnObject, ClickWindow),
            0x0F: (SpawnMob, ConfirmTransaction),
            0x10: (SpawnPainting, CreativeInventoryAction),
            0x11: (SpawnExperienceOrb, EnchantItem),
            0x12: (EntityVelocity, UpdateSign),
            0x13: (DestroyEntities, PlayerAbilities),
            0x14: (Entity, TabComplete),
            0x15: (EntityRelativeMove, ClientSettings),
            0x16: (EntityLook, ClientStatus),
            0x17: (EntityLookAndRelativeMove, None),
            0x18: (EntityTeleport, None),
            0x19: (EntityHeadLook, None),
            0x1A: (EntityStatus, None),
            0x1B: (AttachEntity, None),
            0x1C: (EntityMetadata, None),
            0x1D: (EntityEffect, None),
            0X1E: (RemoveEntityEffect, None),
            0x1F: (SetExperience, None),
            0x20: (EntityProperties, None),
            0x21: (ChunkData, None),
            0x22: (MultiBlockChange, None),
            0x23: (BlockChange, None),
            0x24: (BlockAction, None),
            0x25: (BlockBreakAnimation, None),
            0x26: (MapChunkBulk, None),
            0x27: (Explosion, None),
            0x28: (Effect, None),
            0x29: (SoundEffect, None),
            0x2A: (Particle, None),
            0x2B: (ChangeGameState, None),
            0x2C: (SpawnGlobalEntity, None),
            0x2D: (OpenWindow, None),
            0x2E: (CloseWindow, None),
            0x2F: (SetSlot, None),
            0x30: (WindowItems, None),
            0x31: (WindowProperty, None),
            0x32: (ConfirmTransaction, None),
            0x33: (UpdateSign, None),
            0x34: (Maps, None),
            0x35: (UpdateBlockEntity, None),
            0x36: (SignEditorOpen, None),
            0x37: (Statistics, None),
            0x38: (PlayerListItem, None),
            0x39: (PlayerAbilities, None),
            0x3A: (TabComplete, None),
            0x3B: (ScoreboardObjective, None),
            0x3C: (UpdateScore, None),
            0x3D: (DisplayScoreboard, None),
            0x3E: (Teams, None),
            0x3F: (PluginMessage, None),
            0x40: (Disconnect, None)
        }

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
                print("Received Play: " + self.play_message_delegates[message_id][0].__name__)
                self.play_message_delegates[message_id][0](message_buffer).parse()
            elif self.current_state == NetworkState.login:
                print("Received Login: " + self.login_message_delegates[message_id][0].__name__)
                self.login_message_delegates[message_id][0](message_buffer).parse()
            elif self.current_state == NetworkState.handshake:
                print("Received Handshake: " + self.handshake_message_delegates[message_id][0].__name__)
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
        print("Now state: " + newstate.name)
        self.current_state = newstate

    def send_message(self, message_id, *args):
        # Needs to create io.BytesIO() buffer for message to write to
        # Needs to use _create_varint() to create varint ID and message length
        # Needs to lock? (depends if transport is thread-safe)
        write_buffer = io.BytesIO()
        if self.current_state == NetworkState.play:
            print("Sending Play: " + self.play_message_delegates[message_id][1].__name__)
            self.play_message_delegates[message_id][1](write_buffer).write(*args)
        elif self.current_state == NetworkState.login:
            print("Sending Login: " + self.login_message_delegates[message_id][1].__name__)
            self.login_message_delegates[message_id][1](write_buffer).write(*args)
        elif self.current_state == NetworkState.handshake:
            print("Sending Handshake: " + self.handshake_message_delegates[message_id][1].__name__)
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
