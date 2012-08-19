# http://www.wiki.vg/minecraft/alpha/protocol
# implementation by Treeki

# position info:
# X+1 = south
# X-1 = north
#
# Y+1 = up
# Y-1 = down
#
# Z+1 = west
# Z-1 = east

import select
import socket
import struct
import sys
import time
import urllib.request
import urllib.parse

s_byte = struct.Struct('>b')
s_short = struct.Struct('>h')
s_int = struct.Struct('>i')
s_long = struct.Struct('>q')
s_float = struct.Struct('>f')
s_double = struct.Struct('>d')

verbose = False


def create_session(username, password, version=12):
	e_username = urllib.parse.quote_plus(username)
	e_password = urllib.parse.quote_plus(password)
	url = 'http://www.minecraft.net/game/getversion.jsp?user=%s&password=%s&version=%d'
	url = url % (e_username, e_password, version)
	
	request = urllib.request.urlopen(url)
	data = request.read().decode('utf-8')
	data = data.split(':')
	
	print('Minecraft.net session created.')
	print('Game version: ' + data[0])
	print('Download ticket: ' + data[1])
	print('Username: ' + data[2])
	print('Session ID: ' + data[3])
	
	return data[3]


def create_writer_for_packet_id(id):
	# shortcut function
	w = MCWriter()
	w.write_byte(id)
	return w


class NotEnoughDataError(RuntimeError):
	pass


class MCEntity:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0
		
		self.yaw = 0
		self.pitch = 0
		self.roll = 0
		
		self.type = 'normal'
	
	def move(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	
	def move_relative(self, x, y, z):
		self.x += x
		self.y += y
		self.z += z
	
	def look(self, yaw, pitch):
		self.yaw = yaw
		self.pitch = pitch
	
	def rotate(self, yaw, pitch, roll):
		self.yaw = yaw
		self.pitch = pitch
		self.roll = roll
	
	def __repr__(self):
		s = 'Pos: %d,%d,%d; Rot: %d,%d,%d; Type: %s'
		s = s % (self.x, self.y, self.z, self.yaw, self.pitch, self.roll, self.type)
		
		if self.type == 'named':
			s += ' -- Name: %s; HeldItem: %d' % (self.name, self.held_item)
		elif self.type == 'pickup':
			s += ' -- Type: %d; Count: %d' % (self.pickup_type, self.count)
		elif self.type == 'vehicle':
			s += ' -- Type: %d' % self.vehicle_type
		elif self.type == 'mob':
			s += ' -- Type: %d' % self.mob_type
		
		return s


class MCReader:
	def __init__(self, data):
		self.data = data
		self.length = len(data)
		self.pos = 0
	
	def read_byte(self):
		if self.pos + 0 >= self.length:
			raise NotEnoughDataError
		
		d = s_byte.unpack(self.data[self.pos:self.pos+1])[0]
		self.pos += 1
		return d
	
	def read_short(self):
		if self.pos + 1 >= self.length:
			raise NotEnoughDataError
		
		d = s_short.unpack(self.data[self.pos:self.pos+2])[0]
		self.pos += 2
		return d
	
	def read_int(self):
		if self.pos + 3 >= self.length:
			raise NotEnoughDataError
		
		d = s_int.unpack(self.data[self.pos:self.pos+4])[0]
		self.pos += 4
		return d
	
	def read_long(self):
		if self.pos + 7 >= self.length:
			raise NotEnoughDataError
		
		d = s_long.unpack(self.data[self.pos:self.pos+8])[0]
		self.pos += 8
		return d
	
	def read_float(self):
		if self.pos + 3 >= self.length:
			raise NotEnoughDataError
		
		d = s_float.unpack(self.data[self.pos:self.pos+4])[0]
		self.pos += 4
		return d
	
	def read_double(self):
		if self.pos + 7 >= self.length:
			raise NotEnoughDataError
		
		d = s_double.unpack(self.data[self.pos:self.pos+8])[0]
		self.pos += 8
		return d
	
	def read_string(self):
		string_length = self.read_short()
		assert string_length >= 0
		
		if self.pos + string_length - 1 >= self.length:
			raise NotEnoughDataError
		
		string = self.data[self.pos:self.pos+string_length].decode('utf-8')
		self.pos += string_length
		
		return string
	
	def read_bool(self):
		if self.pos + 0 >= self.length:
			raise NotEnoughDataError
		
		return bool(self.read_byte())
	
	def read_bytes(self, count):
		if self.pos + count - 1 >= self.length:
			raise NotEnoughDataError
		
		data = self.data[self.pos:self.pos+count]
		self.pos += count
		
		return data


class MCWriter:
	def __init__(self):
		self.data = bytes()
	
	def write_byte(self, value):
		self.data += s_byte.pack(value)
	
	def write_short(self, value):
		self.data += s_short.pack(value)
	
	def write_int(self, value):
		self.data += s_int.pack(value)
	
	def write_long(self, value):
		self.data += s_long.pack(value)
	
	def write_float(self, value):
		self.data += s_float.pack(value)
	
	def write_double(self, value):
		self.data += s_double.pack(value)
	
	def write_string(self, value):
		enc_string = value.encode('utf-8')
		self.write_short(len(enc_string))
		self.data += enc_string
	
	def write_bool(self, value):
		self.write_byte(1 if value else 0)
	
	def write_bytes(self, value):
		self.data += value


class MinecraftProtocol():
	def __init__(self, username, password, server, port, server_pass=''):
		self.socket = None
		self.username = username
		self.password = password
		self.server = server
		self.port = port
		self.server_pass = server_pass
		self.session_id = None
		
		self.block_interval = 5
		self.block_queue = []
	
	def connect(self):
		self.entities = {}
		
		self.buffer = bytes()
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.server, self.port))
		self.socket.setblocking(0)
		
		self.send_handshake(self.username)
		
		cur_time = time.time()
		target_time = cur_time + 1
		
		while True:
			cur_time = time.time()
			if cur_time > target_time:
				target_time += 1
				self.second_passed()
			
			can_read, can_write, can_error = select.select([self.socket], [], [], 0.1)
			
			if self.socket in can_read:
				packet = self.socket.recv(128)
				if len(packet) == 0:
					print('Something went wrong with the socket! Received an empty packet.')
					break
				
				self.buffer += packet
				
				do_more = True
				while do_more:
					do_more = self.process_packet()
		
		self.socket.close()
	
	def process_packet(self):
		# try to read a packet from the server
		# if it succeeded, return True
		# if we don't have enough data for the full packet, then return False
		
		reader = MCReader(self.buffer)
		
		try:
			packet_id = reader.read_byte()
			self.process_packet_data(packet_id, reader)
			
			# if we got here, that means it was read correctly
			# cut off this packet
			self.buffer = self.buffer[reader.pos:]
			
			return True
		except NotEnoughDataError:
			# oops
			return False
	
	def process_packet_data(self, id, reader):
		if id == 0x00:
			self.send_packet(b'\0')
		elif id == 0x01:
			self.read_login_response(reader)
		elif id == 0x02:
			self.read_handshake(reader)
		elif id == 0x03:
			self.read_chat_message(reader)
		elif id == 0x04:
			self.read_time_update(reader)
		elif id == 0x05:
			self.read_inventory(reader)
		elif id == 0x06:
			self.read_spawn_position(reader)
		elif id == 0x0D:
			self.read_player_position_and_look(reader)
		elif id == 0x10:
			self.read_set_held_item(reader)
		elif id == 0x11:
			self.read_add_to_inventory(reader)
		elif id == 0x12:
			self.read_arm_animation(reader)
		elif id == 0x14:
			self.read_named_entity_spawn(reader)
		elif id == 0x15:
			self.read_pickup_spawn(reader)
		elif id == 0x16:
			self.read_collect_item(reader)
		elif id == 0x17:
			self.read_add_object_or_vehicle(reader)
		elif id == 0x18:
			self.read_mob_spawn(reader)
		elif id == 0x1D:
			self.read_destroy_entity(reader)
		elif id == 0x1E:
			self.read_entity(reader)
		elif id == 0x1F:
			self.read_entity_relative_move(reader)
		elif id == 0x20:
			self.read_entity_look(reader)
		elif id == 0x21:
			self.read_entity_look_and_relative_move(reader)
		elif id == 0x22:
			self.read_entity_teleport(reader)
		elif id == 0x32:
			self.read_pre_chunk(reader)
		elif id == 0x33:
			self.read_map_chunk(reader)
		elif id == 0x34:
			self.read_multi_block_change(reader)
		elif id == 0x35:
			self.read_block_change(reader)
		elif id == 0x3B:
			self.read_complex_entity(reader)
		elif id == -1:
			self.read_kick(reader)
		else:
			# oops
			print('UNKNOWN PACKET 0x%02x!! Here\'s the buffer: %s' % (id, repr(self.buffer)))
	
	def send_packet(self, packet):
		sent = 0
		while sent < len(packet):
			sent += self.socket.send(packet[sent:])
	
	############################################################################
	# Server => Client Packet Parsing
	############################################################################
	
	def read_login_response(self, reader):
		# server to client packet 0x01: login response
		unk1 = reader.read_int()
		unk2 = reader.read_string()
		unk3 = reader.read_string()
		print('Recv: 0x01 Login Response: %d, %s, %s' % (unk1, repr(unk2), repr(unk3)))
	
	def read_handshake(self, reader):
		# server to client packet 0x02: handshake
		conn_hash = reader.read_string()
		print('Recv: 0x02 Handshake: connection hash: %s' % conn_hash)
		
		if conn_hash != '-' and conn_hash != '+':
			e_username = urllib.parse.quote_plus(self.username)
			e_hash = urllib.parse.quote_plus(conn_hash)
			e_session_id = urllib.parse.quote_plus(self.session_id)
			
			url = 'http://www.minecraft.net/game/joinserver.jsp?user=%s&sessionId=%s&serverId=%s'
			url = url % (e_username, e_session_id, e_hash)
			
			request = urllib.request.urlopen(url)
			print('Identified with minecraft.net. Joinserver.jsp returned: %s' % request.read())
		
		self.send_login_request(2, self.username, self.server_pass)
	
	def read_chat_message(self, reader):
		# server to client packet 0x03: chat message
		message = reader.read_string()
		print('Recv: 0x03 Chat Message: %s' % message)
		
		self.parse_chat(message)
	
	def read_time_update(self, reader):
		# server to client packet 0x04: time update
		time = reader.read_long()
		
		if verbose:
			print('Recv: 0x04 Time Update: %d' % time)
	
	def read_inventory(self, reader):
		# server to client packet 0x05: inventory
		inv_type = reader.read_int()
		count = reader.read_short()
		
		if inv_type == -1:
			print('Recv: 0x05 Inventory: Main Inventory (should have 36 slots; server claims %d):' % count)
		elif inv_type == -2:
			print('Recv: 0x05 Inventory: Equipped Armour (should have 4 slots; server claims %d):' % count)
		elif inv_type == -3:
			print('Recv: 0x05 Inventory: Crafting Slots (should have 4 slots; server claims %d):' % count)
		
		inventory = [None] * count
		for i in range(count):
			item_id = reader.read_short()
			if item_id != -1:
				count = reader.read_byte()
				health = reader.read_short()
				inventory[i] = (item_id, count, health)
		
		print(inventory)
	
	def read_spawn_position(self, reader):
		# server to client packet 0x06: spawn position
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		print('Recv: 0x06 Spawn Position: %d,%d,%d' % (x,y,z))
	
	def read_player_position_and_look(self, reader):
		# server to client packet 0x0D: player position & look
		x = reader.read_double()
		stance = reader.read_double()
		y = reader.read_double()
		z = reader.read_double()
		
		yaw = reader.read_float()
		pitch = reader.read_float()
		
		on_ground = reader.read_bool()
		
		print('Recv: 0x0D Player Position & Look: Position: %f,%f,%f; Stance: %f; Yaw: %f; Pitch: %f; OnGround: %s' % (x,y,z,stance,yaw,pitch,repr(on_ground)))
	
	def read_set_held_item(self, reader):
		# server to client packet 0x10: set held item
		eid = reader.read_int()
		item_type = reader.read_short()
		
		e = self.get_entity(eid)
		e.held_item = item_type
		
		print('Recv: 0x10 Set Held Item: Entity %d is now holding item %d' % (eid, item_type))
	
	def read_add_to_inventory(self, reader):
		# server to client packet 0x11: add to inventory
		item_type = reader.read_short()
		count = reader.read_byte()
		health = reader.read_short()
		
		print('Recv: 0x11 Add To Inventory: Item Type: %d; Count: %d; Health: %d' % (item_type, count, health))
	
	def read_arm_animation(self, reader):
		# server to client packet 0x12: arm animation
		eid = reader.read_int()
		animate = reader.read_bool()
		
		print('Recv: 0x12 Arm Animation: Player %d; Animate: %s' % (eid, repr(animate)))
	
	def read_named_entity_spawn(self, reader):
		# server to client packet 0x14: named entity spawn
		eid = reader.read_int()
		name = reader.read_string()
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		item = reader.read_short()
		
		e = self.add_entity(eid)
		e.type = 'named'
		e.name = name
		e.move(x, y, z)
		e.look(yaw, pitch)
		e.held_item = item
		
		print('Recv: 0x14 Named Entity Spawn: Player %d; Name: %s; Position: %d,%d,%d; Yaw: %d; Pitch: %d; Current Item: %d' % (eid, name, x, y, z, yaw, pitch, item))
	
	def read_pickup_spawn(self, reader):
		# server to client packet 0x15: pickup spawn
		eid = reader.read_int()
		item_type = reader.read_short()
		count = reader.read_byte()
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		roll = reader.read_byte()
		
		e = self.add_entity(eid)
		e.type = 'pickup'
		e.pickup_type = item_type
		e.count = count
		e.move(x, y, z)
		e.rotate(yaw, pitch, roll)
		
		print('Recv: 0x15 Pickup Spawn: Entity %d; Type: %d; Count: %d; Position: %d,%d,%d; Rotation: %d,%d,%d' % (eid, item_type, count, x, y, z, yaw, pitch, roll))
	
	def read_collect_item(self, reader):
		# server to client packet 0x16: collect item
		collected = reader.read_int()
		collector = reader.read_int()
		
		print('Recv: 0x16 Collect Item: Entity %d collected by entity %d' % (collected, collector))
	
	def read_add_object_or_vehicle(self, reader):
		# server to client packet 0x17: add object/vehicle
		eid = reader.read_int()
		type = reader.read_byte()
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		
		e = self.add_entity(eid)
		e.type = 'vehicle'
		e.vehicle_type = type
		e.move(x, y, z)
		
		print('Recv: 0x17 Add Object/Vehicle: Entity %d; Type: %d; Position: %d,%d,%d' % (eid, type, x, y, z))
	
	def read_mob_spawn(self, reader):
		# server to client packet 0x18: mob spawn
		eid = reader.read_int()
		type = reader.read_byte()
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		
		e = self.add_entity(eid)
		e.type = 'mob'
		e.mob_type = type
		e.move(x, y, z)
		e.look(yaw, pitch)
		
		print('Recv: 0x18 Mob Spawn: Entity %d; Type: %d; Position: %d,%d,%d; Rotation: %d,%d' % (eid, type, x, y, z, yaw, pitch))
	
	def read_destroy_entity(self, reader):
		# server to client packet 0x1D: destroy entity
		eid = reader.read_int()
		
		self.remove_entity(eid)
		
		print('Recv: 0x1D Destroy Entity: Entity %d' % eid)
	
	def read_entity(self, reader):
		# server to client packet 0x1E: entity
		eid = reader.read_int()
		
		self.add_entity(eid)
		
		#print('Recv: 0x1E Entity: Entity %d' % eid)
	
	def read_entity_relative_move(self, reader):
		# server to client packet 0x1F: entity relative move
		eid = reader.read_int()
		x = reader.read_byte()
		y = reader.read_byte()
		z = reader.read_byte()
		
		e = self.get_entity(eid)
		e.move_relative(x, y, z)
		
		if verbose:
			print('Recv: 0x1F Entity Relative Move: Entity %d; Relative Position: %d,%d,%d' % (eid, x, y, z))
	
	def read_entity_look(self, reader):
		# server to client packet 0x20: entity look
		eid = reader.read_int()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		
		e = self.get_entity(eid)
		e.look(yaw, pitch)
		
		if verbose:
			print('Recv: 0x20 Entity Look: Entity %d; Yaw: %d; Pitch: %d' % (eid, yaw, pitch))
	
	def read_entity_look_and_relative_move(self, reader):
		# server to client packet 0x21: entity look and relative move
		eid = reader.read_int()
		x = reader.read_byte()
		y = reader.read_byte()
		z = reader.read_byte()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		
		e = self.get_entity(eid)
		e.move_relative(x, y, z)
		e.look(yaw, pitch)
		
		if verbose:
			print('Recv: 0x21 Entity Look and Relative Move: Entity %d; Relative Position: %d,%d,%d; Yaw: %d; Pitch: %d' % (eid, x, y, z, yaw, pitch))
	
	def read_entity_teleport(self, reader):
		# server to client packet 0x22: entity teleport
		eid = reader.read_int()
		x = reader.read_int()
		y = reader.read_int()
		z = reader.read_int()
		yaw = reader.read_byte()
		pitch = reader.read_byte()
		
		e = self.get_entity(eid)
		e.move(x, y, z)
		e.look(yaw, pitch)
		
		print('Recv: 0x22 Entity Teleport: Entity %d; Position: %d,%d,%d; Yaw: %d; Pitch: %d' % (eid, x, y, z, yaw, pitch))
	
	def read_pre_chunk(self, reader):
		# server to client packet 0x32: pre-chunk
		x = reader.read_int()
		z = reader.read_int()
		mode = reader.read_bool()
		
		if verbose:
			if mode:
				print('Recv: 0x32 Pre-Chunk: X: %d; Z: %d; this chunk should be initialised' % (x, z))
			else:
				print('Recv: 0x32 Pre-Chunk: X: %d; Z: %d; this chunk should be unloaded' % (x, z))
	
	def read_map_chunk(self, reader):
		# server to client packet 0x33: map chunk
		x = reader.read_int()
		y = reader.read_short()
		z = reader.read_int()
		size_x = reader.read_byte() + 1
		size_y = reader.read_byte() + 1
		size_z = reader.read_byte() + 1
		compressed_chunk_size = reader.read_int()
		
		# we don't parse this yet
		compressed_chunk = reader.read_bytes(compressed_chunk_size)
		
		if verbose:
			print('Recv: 0x33 Map Chunk: Position: %d,%d,%d; Size: %dx%dx%d; Compressed Data Size: %d' % (x, y, z, size_x, size_y, size_z, compressed_chunk_size))
	
	def read_multi_block_change(self, reader):
		# server to client packet 0x34: multi block change
		chunk_x = reader.read_int()
		chunk_z = reader.read_int()
		array_size = reader.read_short()
		
		# skip past these...
		coord_array = reader.read_bytes(array_size * 2)
		type_array = reader.read_bytes(array_size)
		metadata_array = reader.read_bytes(array_size)
		
		print('Recv: 0x34: Multi Block Change: Chunk X: %d; Chunk Z: %d; Array Size: %d' % (chunk_x, chunk_z, array_size))
	
	def read_block_change(self, reader):
		# server to client packet 0x35: block change
		x = reader.read_int()
		y = reader.read_byte()
		z = reader.read_int()
		type = reader.read_byte()
		metadata = reader.read_byte()
		
		print('Recv: 0x35: Block Change: Position: %d,%d,%d; Type: %d; Metadata: %d' % (x, y, z, type, metadata))
	
	def read_complex_entity(self, reader):
		# server to client packet 0x3B: complex entity
		x = reader.read_int()
		y = reader.read_short()
		z = reader.read_int()
		payload_size = reader.read_short()
		payload = reader.read_bytes(payload_size)
		
		print('Recv: 0x3B: Complex Entity: Position: %d,%d,%d; Payload Size: %d' % (x, y, z, payload_size))
	
	def read_kick(self, reader):
		# server to client packet 0xFF (or -1): kick
		reason = reader.read_string()
		print('Recv:   -1 Kick: reason: %s' % reason)
	
	############################################################################
	# Client => Server Packet Writing
	############################################################################
	
	def send_login_request(self, version, username, server_pass):
		# client to server packet 0x01: login request
		writer = create_writer_for_packet_id(1)
		writer.write_int(version)
		writer.write_string(username)
		writer.write_string(server_pass)
		
		self.send_packet(writer.data)
		print('Sent: 0x01 Login Request: version: %d; username: %s; server pass: %s' % (version, username, server_pass))
	
	def send_handshake(self, username):
		# client to server packet 0x02: handshake
		writer = create_writer_for_packet_id(2)
		writer.write_string(username)
		
		self.send_packet(writer.data)
		print('Sent: 0x02 Handshake: username: %s' % username)
	
	def send_chat_message(self, message):
		# client to server packet 0x03: chat message
		writer = create_writer_for_packet_id(3)
		writer.write_string(message)
		
		self.send_packet(writer.data)
		print('Sent: 0x03 Chat Message: message: %s' % message)
	
	def send_player_inventory(self, type, items):
		# client to server packet 0x05: player inventory
		writer = create_writer_for_packet_id(5)
		writer.write_int(type)
		writer.write_short(len(items))
		
		for item in items:
			if item == None:
				writer.write_short(-1)
			else:
				writer.write_short(item[0])
				writer.write_byte(item[1])
				writer.write_short(item[2])
		
		self.send_packet(writer.data)
		print('Sent: 0x05 Inventory: type: %d' % type)
	
	def send_player_state(self, on_ground):
		# client to server packet 0x0A: player state
		writer = create_writer_for_packet_id(0x0A)
		writer.write_bool(on_ground)
		
		self.send_packet(writer.data)
		print('Sent: 0x0A Player State: onGround: %s' % repr(on_ground))
	
	def send_player_position(self, x, y, z, stance, on_ground):
		# client to server packet 0x0B: player position
		writer = create_writer_for_packet_id(0x0B)
		writer.write_double(x)
		writer.write_double(y)
		writer.write_double(stance)
		writer.write_double(z)
		writer.write_bool(on_ground)
		
		self.send_packet(writer.data)
		print('Sent: 0x0B Player Position: Position: %f,%f,%f; Stance: %f; onGround: %s' % (x, y, z, stance, repr(on_ground)))
	
	def send_player_look(self, yaw, pitch, on_ground):
		# client to server packet 0x0C: player look
		writer = create_writer_for_packet_id(0x0C)
		writer.write_float(yaw)
		writer.write_float(pitch)
		writer.write_bool(on_ground)
		
		self.send_packet(writer.data)
		print('Sent: 0x0C Player Look: Yaw: %f; Pitch: %f; onGround: %s' % (yaw, pitch, repr(on_ground)))
	
	def send_player_position_and_look(self, x, y, z, stance, yaw, pitch, on_ground):
		# client to server packet 0x0D: player position & look
		writer = create_writer_for_packet_id(0x0B)
		writer.write_double(x)
		writer.write_double(y)
		writer.write_double(stance)
		writer.write_double(z)
		writer.write_float(yaw)
		writer.write_float(pitch)
		writer.write_bool(on_ground)
		
		self.send_packet(writer.data)
		print('Sent: 0x0D Player Position & Look: Position: %f,%f,%f; Stance: %f; Yaw: %f; Pitch: %f; onGround: %s' % (x, y, z, stance, yaw, pitch, repr(on_ground)))
	
	def send_player_digging(self, status, x, y, z, face):
		# client to server packet 0x0E: player digging
		writer = create_writer_for_packet_id(0x0E)
		writer.write_byte(status)
		writer.write_int(x)
		writer.write_byte(y)
		writer.write_int(z)
		writer.write_byte(face)
		
		self.send_packet(writer.data)
		print('Sent: 0x0E Player Digging: Status: %d; Block Position: %d,%d,%d; Face: %d' % (status, x, y, z, face))
	
	def send_player_block_placement(self, id, x, y, z, direction):
		# client to server packet 0x0F: player block placement
		writer = create_writer_for_packet_id(0x0F)
		writer.write_short(id)
		writer.write_int(x)
		writer.write_byte(y)
		writer.write_int(z)
		writer.write_byte(direction)
		
		self.send_packet(writer.data)
		print('Sent: 0x0F Player Block Placement: Id: %d; Block Position: %d,%d,%d; Direction: %d' % (id, x, y, z, direction))
	
	def send_holding_change(self, id):
		# client to server packet 0x10: holding change
		writer = create_writer_for_packet_id(0x10)
		writer.write_int(12345678) # unused?
		writer.write_short(id)
		
		self.send_packet(writer.data)
		print('Sent: 0x10 Holding Change: Id: %d' % id)
	
	def send_disconnect(self, reason):
		# client to server packet 0xFF (or -1): reason
		writer = create_writer_for_packet_id(-1)
		writer.write_string(reason)
		
		self.send_packet(writer.data)
		print('Sent:   -1 Disconnect: Reason: %s' % reason)
	
	
	############################################################################
	# Entity Management
	############################################################################
	
	def add_entity(self, id):
		if id in self.entities:
			return self.entities[id]
		
		e = MCEntity()
		self.entities[id] = e
		return e
	
	def get_entity(self, id):
		return self.add_entity(id) # it does the same thing
	
	def remove_entity(self, id):
		if id not in self.entities:
			return
		
		del self.entities[id]
		
	############################################################################
	# Chat and Other Processing
	############################################################################
	
	def second_passed(self):
		# process block queue
		if len(self.block_queue) > 0:
			to_do = []
			for i in range(self.block_interval):
				if len(self.block_queue) == 0:
					break
				to_do.append(self.block_queue.pop())
			
			for x, y, z, id in to_do:
				if id == -1:
					self.send_player_digging(3, x, y, z + 1, 2)
				else:
					self.send_player_block_placement(id, x, y, z, 2)
			
			if len(self.block_queue) == 0:
				self.send_chat_message('Queue complete!')
	
	def parse_chat(self, message):
		if message.startswith('[IRC] '):
			message = message[6:]
		
		if message[0] != '<' or '>' not in message:
			# probably not a chat message
			return
		
		name = message[1:message.find('>')]
		message = message[message.find('>') + 2:]
		
		# strip colours off the name
		if name[0] == '§':
			name = name[2:-2]
		
		# now process it
		print('Got message by %s: %s' % (name, message))
		
		if message[0] == '!':
			# it's a command!
			if ' ' in message:
				cmd = message[1:message.find(' ')]
				args = message[message.find(' ')+1:]
			else:
				cmd = message[1:]
				args = None
			
			if cmd == 'findEntityByName':
				for id, e in self.entities.items():
					if e.type == 'named':
						print('Matching %s against %s' % (repr(e.name), repr(args)))
						if e.name == args:
							self.send_chat_message('Found entity: ID %d' % id)
							return
				
				# didn't find it
				self.send_chat_message('Entity not found')
			
			if cmd == 'getEntityInfo':
				id = int(args)
				if id in self.entities:
					e = self.entities[id]
					self.send_chat_message(repr(e))
				else:
					self.send_chat_message('Entity not found')
			
			if cmd == 'quit':
				self.send_disconnect('bye')
				sys.exit()
			
			if cmd == 'placeWithDir':
				id, x, y, z, direction = map(int, args.split(' '))
				self.send_player_block_placement(id, x, y, z, direction)
			
			if cmd == 'place':
				id, pos = args.split(' ')
				id = int(id)
				x,y,z = map(int, pos.split(','))
				self.send_player_block_placement(id, x, y, z + 1, 2)
			
			if cmd == 'destroy':
				states, pos = args.split(' ')
				states = map(int, states.split(','))
				x,y,z = map(int, pos.split(','))
				for s in states:
					self.send_player_digging(s, x, y, z, 2)
			
			if cmd == 'fillRect':
				id, pos1, pos2 = args.split(' ')
				id = int(id)
				x1,y1,z1 = map(int, pos1.split(','))
				x2,y2,z2 = map(int, pos2.split(','))
				
				if y1 != y2:
					self.send_chat_message('WARNING: Y positions do not match! I\' refuse to fill this area!')
					return
				
				# preview the corners
				self.send_player_block_placement(id, x1, y1, z1 + 1, 2)
				self.send_player_block_placement(id, x2, y1, z1 + 1, 2)
				self.send_player_block_placement(id, x1, y1, z2 + 1, 2)
				self.send_player_block_placement(id, x2, y1, z2 + 1, 2)
				
				self.send_chat_message('I\'ve placed blocks at each corner. If this rect is correct, then use !fillRect2 to confirm it.')
			
			if cmd == 'fillRect2':
				id, pos1, pos2 = args.split(' ')
				id = int(id)
				x1,y1,z1 = map(int, pos1.split(','))
				x2,y2,z2 = map(int, pos2.split(','))
				
				if y1 != y2:
					self.send_chat_message('WARNING: Y positions do not match! I\' refuse to fill this area!')
					return
				
				# sort it out
				minX = min(x1, x2)
				minZ = min(z1, z2)
				maxX = max(x1, x2)
				maxZ = max(z1, z2)
				
				# add every block to the queue
				for x in range(minX, maxX+1):
					for z in range(minZ, maxZ+1):
						self.block_queue.append((x, y1, z, id))
				
				self.send_chat_message('Fill started! %d blocks in queue; estimated time is %d seconds.' % (len(self.block_queue), len(self.block_queue) / self.block_interval))
			
			if cmd == 'queueStatus':
				self.send_chat_message('Block interval is %d. %d blocks in queue; estimated time is %d seconds.' % (self.block_interval, len(self.block_queue), len(self.block_queue) / self.block_interval))
			
			if cmd == 'setBlockInterval':
				self.block_interval = int(args)
				self.send_chat_message('Interval changed to %d! %d blocks in queue; new estimated time is %d seconds.' % (self.block_interval, len(self.block_queue), len(self.block_queue) / self.block_interval))
			
			if cmd == 'clearQueue':
				self.block_queue = []
				self.send_chat_message('Cleared block queue.')


session_id = create_session(sys.argv[1], sys.argv[2])

p = MinecraftProtocol(sys.argv[1], sys.argv[2], 'xxxxx', 25565)
p.session_id = session_id
p.connect()
