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
import gzip
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

import mipybot.networking
import mipybot.player
import mipybot.chat
import mipybot.world.items
import mipybot.windows

from third_party import pynbt

class Message:
    read_buffer = io.BytesIO()
    write_buffer = io.BytesIO()

    # Raw reading and writing

    def read_raw(length):
        return Message.read_buffer.read(length)

    def write_raw(data):
        Message.write_buffer.write(data)

    # Struct convenience methods

    def _struct_read(struct_format, length):
        return struct.unpack(struct_format, Message.read_raw(length))[0]

    def _struct_write(struct_format, value):
        Message.write_raw(struct.pack(struct_format, value))

    # bool

    def read_bool():
        return Message._struct_read("?", 1)

    def write_bool(value):
        Message._struct_write("?", value)

    # byte

    def read_byte():
        return Message._struct_read("b", 1)

    def write_byte(value):
        Message._struct_write("b", value)

    # ubyte

    def read_ubyte():
        return Message._struct_read("B", 1)

    def write_ubyte(value):
        Message._struct_write("B", value)

    # short

    def read_short():
        return Message._struct_read("!h", 2)

    def write_short(value):
        Message._struct_write("!h", value)

    # ushort

    def read_ushort():
        return Message._struct_read("!H", 2)

    def write_ushort(value):
        Message._struct_write("!H", value)

    # int

    def read_int():
        return Message._struct_read("!i", 4)

    def write_int(value):
        Message._struct_write("!i", value)

    # uint

    def read_uint():
        return Message._struct_read("!I", 4)

    def write_uint(value):
        Message._struct_write("!I", value)

    # long

    def read_long():
        return Message._struct_read("!q", 8)

    def write_long(value):
        Message._struct_write("!q", value)

    # ulong

    def read_ulong():
        return Message._struct_read("!Q", 8)

    def write_ulong(value):
        Message._struct_write("!Q", value)

    # float

    def read_float():
        return Message._struct_read("!f", 4)

    def write_float(value):
        Message._struct_write("!f", value)

    # double

    def read_double():
        return Message._struct_read("!d", 8)

    def write_double(value):
        Message._struct_write("!d", value)

    # 128-bit integer

    def read_128int():
        return uuid.UUID(bytes=Message.read_raw(16)).int

    def write_128int(value):
        Message.write_raw(uuid.UUID(int=value).bytes)

    # varint

    def read_varint():
        d = 0
        for i in range(5):
            b = ord(Message.read_raw(1))
            d |= (b & 0x7F) << 7*i
            if not b & 0x80:
                break
        return d

    def write_varint(d):
        o = bytes()
        while True:
            b = d & 0x7F
            d >>= 7
            o += struct.pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        Message.write_raw(o)

    # string

    def read_string():
        str_len = Message.read_varint()
        return Message.read_raw(str_len).decode("UTF-8")

    def write_string(value):
        encoded_string = value.encode("UTF-8")
        Message.write_varint(len(encoded_string))
        Message.write_raw(encoded_string)

    # slot

    def read_slot(index=None):
        item_id = Message.read_short()
        if item_id == -1:
            return mipybot.windows.Slot(None, index)
        else:
            item_type = mipybot.world.items.ItemTypes(item_id)
            item_count = Message.read_byte()
            item_damage = Message.read_short()
            metadatalength = Message.read_short()
            if metadatalength == -1:
                enchantments = None
            else:
                enchantments = dict()
                nbt_parser = pynbt.NBTFile(io=io.BytesIO(gzip.decompress(Message.read_raw(metadatalength))))
                for tag_compound in nbt_parser["ench"]:
                    enchantment_type = mipybot.world.items.ItemEnchantments(tag_compound["id"].value)
                    enchantment_level = tag_compound["lvl"].value
                    enchantments[enchantment_type] = enchantment_level
            if item_type in mipybot.world.items.SubclassItemMapping:
                slot_item = mipybot.world.items.SubclassItemMapping[item_type](item_type, item_count, item_damage, enchantments)
            else:
                slot_item = mipybot.world.items.Item(item_type, item_count, item_damage, enchantments)
            slot_obj = mipybot.windows.Slot(slot_item, index)
            return slot_obj

    def write_slot(slot_obj):
        if slot_obj.item is None:
            Message.write_short(-1)
        else:
            Message.write_short(slot_obj.item.type.value)
            Message.write_byte(slot_obj.item.count)
            Message.write_short(slot_obj.item.damage)
            if slot_obj.item.enchantments is None:
                Message.write_short(-1)
            else:
                enchantment_dict = dict()
                nbt_list = list()
                for enchantment_type in slot_obj.item.enchantments:
                    temp_dict = dict()
                    temp_dict["id"] = pynbt.TAG_Short(enchantment_type.value)
                    temp_dict["lvl"] = pynbt.TAG_Short(slot_obj.item.enchantments[enchantment_type])
                    nbt_list.append(temp_dict)
                enchantment_dict["ench"] = pynbt.TAG_List(pynbt.TAG_Compound, nbt_list)
                nbt_writer = pynbt.NBTFile(value=enchantment_dict)
                nbt_data_io = io.BytesIO()
                nbt_writer.save(nbt_data_io)
                nbt_data_io.seek(0)
                nbt_data = nbt_data_io.read()
                nbt_data_io.close()
                Message.write_short(len(nbt_data))
                Message.write_raw(nbt_data)

    # metadata

    def read_metadata():
        # This is a stub
        x = Message.read_ubyte()
        while not x == 127:
            ty = x >> 5
            if ty == 0:
                Message.read_byte()
            if ty == 1:
                Message.read_short()
            if ty == 2:
                Message.read_int()
            if ty == 3:
                Message.read_float()
            if ty == 4:
                Message.read_string()
            if ty == 5:
                Message.read_slot()
            if ty == 6:
                Message.read_int()
                Message.read_int()
                Message.read_int()
            x = Message.read_ubyte()

    def write_metadata():
        raise NotImplementedError()

    def read_json():
        return json.dumps(Message.read_string())

    # Methods to override per-message

    def parse():
        raise NotImplementedError()

    def write(*args):
        raise NotImplementedError()

# Login and Play

class Disconnect:
    def parse():
        print("Received disconnect: " + Message.read_json())

# Handshake Messages

class Handshake:
    def write():
        Message.write_varint(5) # 1.7.6 through 1.7.10
        if mipybot.networking.NetworkManager.host_spoof is None:
            Message.write_string(mipybot.networking.NetworkManager.host)
        else:
            Message.write_string(mipybot.networking.NetworkManager.host_spoof)
        if mipybot.networking.NetworkManager.port_spoof is None:
            Message.write_ushort(mipybot.networking.NetworkManager.port)
        else:
            Message.write_ushort(mipybot.networking.NetworkManager.port_spoof)
        Message.write_varint(2) # Login status

# Login Messages

class EncryptionRequest:
    def parse():
        Message.read_string() # Server ID
        encoded_public_key_len = Message.read_short()
        Encryption.set_encoded_public_key(Message.read_raw(encoded_public_key_len))
        verification_token_len = Message.read_short()
        Encryption.set_verification_token(Message.read_raw(verification_token_len))
        Encryption.generate_pkcscipher()
        Encryption.generate_aes()
        Protocol.send_message(0x01)

class LoginSuccess:
    def parse():
        print("UUID: " + Message.read_string())
        print("Username: " + Message.read_string())
        Protocol.set_current_state(NetworkState.play)

class LoginStart:
    def write():
        Message.write_string(mipybot.player.PlayerManager.player_name)

class EncryptionResponse:
    def write():
        encrypted_aes_key = Encryption.pkcs_encrypt(Encryption.aes_key)
        Message.write_short(len(encrypted_aes_key))
        Message.write_raw(encrypted_aes_key)
        encrypted_verification_token = Encryption.pkcs_encrypt(Encryption.verification_token)
        Message.write_short(len(encrypted_verification_token))
        Message.write_raw(encrypted_verification_token)
        Encryption.enable_encryption()

# Play Messages

class KeepAlive:
    def parse():
        Protocol.send_message(0x00, Message.read_int())

    def write(keep_alive_id):
        Message.write_int(keep_alive_id)

class JoinGame:
    def parse():
        Message.read_int() # Player Entity ID
        Message.read_ubyte() # Gamemode
        Message.read_byte() # Dimension
        Message.read_ubyte() # Difficulty
        Message.read_ubyte() # Max players, for drawing player list
        Message.read_string() # Level type
        Protocol.send_message(0x15) # ClientSettings

class ChatMessage:
    def parse():
        mipybot.chat.ChatManager.process_chat(Message.read_string())

    def write(message):
        Message.write_string(message)

class TimeUpdate:
    def parse():
        Message.read_long() # Age of the world
        Message.read_long() # Time of the day

class EntityEquipment:
    def parse():
        Message.read_int() # Entity ID
        Message.read_short() # Equipment slot ID
        Message.read_slot() # Equipment item

class SpawnPosition:
    def parse():
        Message.read_int() # Spawn x
        Message.read_int() # Spawn y
        Message.read_int() # Spawn z

class UpdateHealth:
    def parse():
        Message.read_float() # Health
        Message.read_short() # Food
        Message.read_float() # Food saturation

class Respawn:
    def parse():
        Message.read_int() # Dimension
        Message.read_ubyte() # Difficulty
        Message.read_ubyte() # Gamemode
        Message.read_string() # Level type

class PlayerPositionAndLook:
    def parse():
        Message.read_double() # Absolute X
        Message.read_double() # Absolute Y of player eyes
        Message.read_double() # Absolute Z
        Message.read_float() # Yaw in degrees
        Message.read_float() # Pitch in degrees
        Message.read_bool() # On Ground

    def write():
        raise NotImplementedError()

class HeldItemChange:
    def parse():
        Message.read_byte() # Selected slot index

    def write():
        raise NotImplementedError()

class UseBed:
    def parse():
        Message.read_int() # Player entity ID
        Message.read_int() # Bed head-board X
        Message.read_ubyte() # Bed head-board Y
        Message.read_int() # Bed head-board Z

class Animation:
    def parse():
        Message.read_varint() # Player entity ID
        Message.read_ubyte() # Animation ID

    def write():
        raise NotImplementedError()

class SpawnPlayer:
    def parse():
        Message.read_varint() # Player entity ID
        Message.read_string() # Player UUID
        Message.read_string() # Player name
        data_count = Message.read_varint()
        for i in range(data_count):
            Message.read_string() # Name of property
            Message.read_string() # Value of property
            Message.read_string() # Signature of property
        Message.read_int() # Player X as fixed-point number
        Message.read_int() # Player Y as fixed-point number
        Message.read_int() # Player Z as fixed-point number
        Message.read_byte() # Player Yaw
        Message.read_byte() # Player pitch
        Message.read_short() # Current holding item
        Message.read_metadata()

class CollectItem:
    def parse():
        Message.read_int() # Collected entity ID
        Message.read_int() # Collector entity ID

class SpawnObject:
    def parse():
        Message.read_varint() # Entity ID
        Message.read_byte() # Type of object
        Message.read_int() # X as fixed-point number
        Message.read_int() # Y as fixed-point number
        Message.read_int() # Z as fixed-point number
        Message.read_byte() # Pitch
        Message.read_byte() # Yaw
        object_type = Message.read_int()
        if object_type > 0:
            Message.read_short() # Speed X
            Message.read_short() # Speed Y
            Message.read_short() # Speed Z

class SpawnMob:
    def parse():
        Message.read_varint() # Entity ID
        Message.read_ubyte() # Type of mob
        Message.read_int() # X as fixed-point number
        Message.read_int() # Y as fixed-point number
        Message.read_int() # Z as fixed-point number
        Message.read_byte() # Yaw
        Message.read_byte() # Pitch
        Message.read_byte() # Head Pitch
        Message.read_short() # Velocity X
        Message.read_short() # Velocity Y
        Message.read_short() # Velocity Z
        Message.read_metadata()

class SpawnPainting:
    def parse():
        Message.read_varint() # Entity ID
        Message.read_string() # Name of painting
        Message.read_int() # Center X
        Message.read_int() # Center Y
        Message.read_int() # Center Z
        Message.read_int() # Direction

class SpawnExperienceOrb:
    def parse():
        Message.read_varint() # Entity ID
        Message.read_int() # X as fixed-point number
        Message.read_int() # Y as fixed-point number
        Message.read_int() # Z as fixed-point number
        Message.read_short() # Count

class EntityVelocity:
    def parse():
        Message.read_int() # Entity ID
        Message.read_short() # Velocity X
        Message.read_short() # Velocity Y
        Message.read_short() # Velocity Z

class DestroyEntities:
    def parse():
        entity_count = Message.read_byte()
        for i in range(entity_count):
            Message.read_int() # Entity ID

class Entity:
    def parse():
        Message.read_int() # Entity ID

class EntityRelativeMove:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # delta X as fixed-point number
        Message.read_byte() # delta Y as fixed-point number
        Message.read_byte() # delta Z as fixed-point number

class EntityLook:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # Yaw fraction
        Message.read_byte() # Pitch fraction

class EntityLookAndRelativeMove:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # delta X as fixed-point number
        Message.read_byte() # delta Y as fixed-point number
        Message.read_byte() # delta Z as fixed-point number
        Message.read_byte() # Yaw fraction
        Message.read_byte() # Pitch fraction

class EntityTeleport:
    def parse():
        Message.read_int() # Entity ID
        Message.read_int() # X as fixed-point number
        Message.read_int() # Y as fixed-point number
        Message.read_int() # Z as fixed-point number
        Message.read_byte() # Yaw fraction
        Message.read_byte() # Pitch fraction

class EntityHeadLook:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # Yaw

class EntityStatus:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # Entity status

class AttachEntity:
    def parse():
        Message.read_int() # Entity ID
        Message.read_int() # Vehicle Entity ID
        Message.read_bool() # Whether to leash entity to vehicle

class EntityMetadata:
    def parse():
        Message.read_int() # Entity ID
        Message.read_metadata()

class EntityEffect:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # Effect ID
        Message.read_byte() # Amplifier
        Message.read_short() # Duration

class RemoveEntityEffect:
    def parse():
        Message.read_int() # Entity ID
        Message.read_byte() # Effect ID

class SetExperience:
    def parse():
        Message.read_float() # Experience bar
        Message.read_short() # Level
        Message.read_short() # Total experience

class EntityProperties:
    def parse():
        Message.read_int() # Entity ID
        property_count = Message.read_int()
        for i in range(property_count):
            Message.read_string() # Key
            Message.read_double() # Value
            modifier_count = Message.read_short()
            for j in range(modifier_count):
                Message.read_128int() # UUID
                Message.read_double() # Amount
                Message.read_byte() # Operation

class ChunkData:
    def parse():
        Message.read_int() # Chunk X coordinate
        Message.read_int() # Chunk Z coordinate
        Message.read_bool() # Ground-up continuous
        Message.read_ushort() # Primary bit map
        Message.read_ushort() # Add bit map
        chunk_data_length = Message.read_int()
        Message.read_raw(chunk_data_length)

class MultiBlockChange:
    def parse():
        Message.read_int() # Chunk X coordinate
        Message.read_int() # Chunk Z coordinate
        Message.read_short() # number of blocks affected
        record_size = Message.read_int()
        Message.read_raw(record_size)

class BlockChange:
    def parse():
        Message.read_int() # Block X coordinate
        Message.read_ubyte() # Block Y coordinate
        Message.read_int() # Block Z coordinate
        Message.read_varint() # Block ID
        Message.read_ubyte() # Block metadata

class BlockAction:
    def parse():
        Message.read_int() # Block X
        Message.read_short() # Block Y
        Message.read_int() # block Z
        Message.read_ubyte()
        Message.read_ubyte()
        Message.read_varint()

class BlockBreakAnimation:
    def parse():
        Message.read_varint()
        Message.read_int()
        Message.read_int()
        Message.read_int()
        Message.read_byte()

class MapChunkBulk:
    def parse():
        chunk_count = Message.read_short()
        data_length = Message.read_int()
        Message.read_bool()
        Message.read_raw(data_length)
        for i in range(chunk_count):
            Message.read_int()
            Message.read_int()
            Message.read_ushort()
            Message.read_ushort()

class Explosion:
    def parse():
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        record_count = Message.read_int()
        for i in range(record_count):
            Message.read_byte()
            Message.read_byte()
            Message.read_byte()
        Message.read_float()
        Message.read_float()
        Message.read_float()

class Effect:
    def parse():
        Message.read_int()
        Message.read_int()
        Message.read_byte()
        Message.read_int()
        Message.read_int()
        Message.read_bool()

class SoundEffect:
    def parse():
        Message.read_string()
        Message.read_int()
        Message.read_int()
        Message.read_int()
        Message.read_float()
        Message.read_ubyte()

class Particle:
    def parse():
        Message.read_string()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_float()
        Message.read_int()

class ChangeGameState:
    def parse():
        Message.read_ubyte()
        Message.read_float()

class SpawnGlobalEntity:
    def parse():
        Message.read_varint()
        Message.read_byte()
        Message.read_int()
        Message.read_int()
        Message.read_int()

class OpenWindow:
    def parse():
        window_id = Message.read_ubyte()
        window_type = mipybot.windows.WindowTypes[Message.read_ubyte()]
        window_title = Message.read_string()
        slot_count = Message.read_ubyte() # TODO: Use for determining chest size
        is_actual_title = Message.read_bool()
        if window_type == 11:
            Message.read_int()
        mipybot.windows.WindowManager.open(window_type(window_id, window_title))

class CloseWindow:
    def parse():
        window_id = Message.read_ubyte()
        if not window_id == 0:
            mipybot.windows.WindowManager.close(mipybot.windows.WindowManager.windows[window_id], False)

    def write(window_obj):
        Message.write_byte(window_obj.id)

class SetSlot:
    def parse():
        window_id = Message.read_byte()
        slot_index = Message.read_short()
        slot_obj = Message.read_slot(slot_index)
        if (window_id < 0) or (slot_index < 0):
            print("WARNING: Ignoring invalid SetSlot values: " + ", ".join([str(window_id), str(slot_index)]))
        else:
            mipybot.windows.WindowManager.set_slots(window_id, {slot_index: slot_obj})

class WindowItems:
    def parse():
        window_id = Message.read_ubyte()
        slot_count = Message.read_short()
        slot_dict = dict()
        for i in range(slot_count):
            slot_dict[i] = Message.read_slot(i)
        mipybot.windows.WindowManager.set_slots(window_id, slot_dict)

class WindowProperty:
    def parse():
        Message.read_ubyte()
        Message.read_short()
        Message.read_short()

class ConfirmTransaction:
    def parse():
        window_id = Message.read_ubyte()
        action_id = Message.read_short()
        is_accepted = Message.read_bool()
        Protocol.send_message(0x0F, window_id, action_id, True)
        mipybot.windows.WindowManager.confirm_transaction(window_id, is_accepted)

    def write(window_id, action_id, is_accepted):
        Message.write_ubyte(window_id)
        Message.write_short(action_id)
        Message.write_bool(is_accepted)

class UpdateSign:
    def parse():
        Message.read_int()
        Message.read_short()
        Message.read_int()
        Message.read_string()
        Message.read_string()
        Message.read_string()
        Message.read_string()

    def write():
        raise NotImplementedError()

class Maps:
    def parse():
        Message.read_varint()
        data_length = Message.read_short()
        Message.read_raw(data_length)

class UpdateBlockEntity:
    def parse():
        Message.read_int()
        Message.read_short()
        Message.read_int()
        Message.read_ubyte()
        data_length = Message.read_short()
        Message.read_raw(data_length)

class SignEditorOpen:
    def parse():
        Message.read_int()
        Message.read_int()
        Message.read_int()

class Statistics:
    def parse():
        entry_count = Message.read_varint()
        for i in range(entry_count):
            Message.read_string()
            Message.read_varint()

class PlayerListItem:
    def parse():
        Message.read_string()
        Message.read_bool()
        Message.read_short()

class PlayerAbilities:
    def parse():
        Message.read_byte()
        Message.read_float()
        Message.read_float()

    def write():
        raise NotImplementedError()

class TabComplete:
    def parse():
        count = Message.read_varint()
        for i in range(count):
            Message.read_string()

    def write():
        raise NotImplementedError()

class ScoreboardObjective:
    def parse():
        Message.read_string()
        Message.read_string()
        Message.read_byte()

class UpdateScore:
    def parse():
        Message.read_string()
        Message.read_byte()
        Message.read_string()
        Message.read_int()

class DisplayScoreboard:
    def parse():
        Message.read_byte()
        Message.read_string()

class Teams:
    def parse():
        Message.read_string()
        mode = Message.read_byte()
        if (mode is 0) or (mode is 2):
            Message.read_string()
            Message.read_string()
            Message.read_string()
            Message.read_byte()
        if (mode is 0) or (mode is 3) or (mode is 4):
            player_count = Message.read_short()
            for i in range(player_count):
                Message.read_string()

class PluginMessage:
    def parse():
        Message.read_string()
        data_length = Message.read_short()
        Message.read_raw(data_length)

    def write():
        raise NotImplementedError()

class UseEntity:
    def write():
        raise NotImplementedError()

class Player:
    def write():
        raise NotImplementedError()

class PlayerPosition:
    def write():
        raise NotImplementedError()

class PlayerLook:
    def write():
        raise NotImplementedError()

class PlayerDigging:
    def write():
        raise NotImplementedError()

class PlayerBlockPlacement:
    def write():
        raise NotImplementedError()

class EntityAction:
    def write():
        raise NotImplementedError()

class SteerVehicle:
    def write():
        raise NotImplementedError()

class ClickWindow:
    def write(action_number, window_obj, slot_obj, mode, button):
        Message.write_byte(window_obj.id)
        Message.write_short(slot_obj.index)
        Message.write_byte(button)
        Message.write_short(action_number)
        Message.write_byte(mode)
        Message.write_slot(slot_obj)

class CreativeInventoryAction:
    def write():
        raise NotImplementedError()

class EnchantItem:
    def write():
        raise NotImplementedError()

class ClientSettings:
    def write():
        Message.write_string("en_US") # Locale
        Message.write_byte(0) # Far
        Message.write_byte(0) # All chat
        Message.write_bool(False) # Do not want chat colors
        Message.write_byte(2) # Normal difficulty
        Message.write_bool(False) # No need to show cape

class ClientStatus:
    def write():
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
            Message.read_buffer.seek(0)
            Message.read_buffer.truncate(0)
            Message.read_buffer.write(message_data)
            Message.read_buffer.seek(0)
            message_id = yield from self._unpack_varint(Message.read_buffer)
            if self.current_state == NetworkState.play:
                #print("Received Play: " + self.play_message_delegates[message_id][0].__name__)
                self.play_message_delegates[message_id][0].parse()
            elif self.current_state == NetworkState.login:
                #print("Received Login: " + self.login_message_delegates[message_id][0].__name__)
                self.login_message_delegates[message_id][0].parse()
            elif self.current_state == NetworkState.handshake:
                #print("Received Handshake: " + self.handshake_message_delegates[message_id][0].__name__)
                self.handshake_message_delegates[message_id][0].parse()
            else:
                raise Exception("Invalid state" + str(self.current_state))
            remainder_data = self.databuffer.read()
            self.databuffer.truncate(0)
            self.databuffer.seek(0)
            self.databuffer.write(remainder_data)
            self.databuffer.seek(0)
            del remainder_data

    # Public methods

    def set_current_state(self, newstate):
        print("Now state: " + newstate.name)
        self.current_state = newstate

    def send_message(self, message_id, *args):
        # Needs to create io.BytesIO() buffer for message to write to
        # Needs to use _create_varint() to create varint ID and message length
        # Needs to lock? (depends if transport is thread-safe)
        Message.write_buffer.seek(0)
        Message.write_buffer.truncate(0)
        if self.current_state == NetworkState.play:
            #print("Sending Play: " + self.play_message_delegates[message_id][1].__name__)
            self.play_message_delegates[message_id][1].write(*args)
        elif self.current_state == NetworkState.login:
            #print("Sending Login: " + self.login_message_delegates[message_id][1].__name__)
            self.login_message_delegates[message_id][1].write(*args)
        elif self.current_state == NetworkState.handshake:
            #print("Sending Handshake: " + self.handshake_message_delegates[message_id][1].__name__)
            self.handshake_message_delegates[message_id][1].write(*args)
        else:
            raise Exception("Invalid state" + str(self.current_state))
        Message.write_buffer.seek(0)
        message_data = self._create_varint(message_id) + Message.write_buffer.read()
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
