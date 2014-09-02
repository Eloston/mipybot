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

import mipybot.world.items

class Block:
    def __init__(self, block_type, position):
        self.type = block_type
        self.position = position

    def set_block_metadata(self, *args):
        # Block metadata and Block Entity (aka Tile Entity)
        raise NotImplementedError()

class BlockTypes(enum.Enum):
    air = 0
    stone = 1
    grass = 2
    dirt = 3
    cobblestone = 4
    planks = 5
    sapling = 6
    bedrock = 7
    flowing_water = 8
    water = 9
    flowing_lava = 10
    lava = 11
    sand = 12
    gravel = 13
    gold_ore = 14
    iron_ore = 15
    coal_ore = 16
    log = 17
    leaves = 18
    sponge = 19
    glass = 20
    lapis_ore = 21
    lapis_block = 22
    dispenser = 23
    sandstone = 24
    noteblock = 25
    bed = 26
    golden_rail = 27
    detector_rail = 28
    sticky_piston = 29
    web = 30
    tallgrass = 31
    deadbush = 32
    piston = 33
    piston_head = 34
    wool = 35
    piston_extension = 36
    yellow_flower = 37
    red_flower = 38
    brown_mushroom = 39
    red_mushroom = 40
    gold_block = 41
    iron_block = 42
    double_stone_slab = 43
    stone_slab = 44
    brick_block = 45
    tnt = 46
    bookshelf = 47
    mossy_cobblestone = 48
    obsidian = 49
    torch = 50
    fire = 51
    mob_spawner = 52
    oak_stairs = 53
    chest = 54
    redstone_wire = 55
    diamond_ore = 56
    diamond_block = 57
    crafting_table = 58
    wheat = 59
    farmland = 60
    furnace = 61
    lit_furnace = 62
    standing_sign = 63
    wooden_door = 64
    ladder = 65
    rail = 66
    stone_stairs = 67
    wall_sign = 68
    lever = 69
    stone_pressure_plate = 70
    iron_door = 71
    wooden_pressure_plate = 72
    redstone_ore = 73
    lit_redstone_ore = 74
    unlit_redstone_torch = 75
    redstone_torch = 76
    stone_button = 77
    snow_layer = 78
    ice = 79
    snow = 80
    cactus = 81
    clay = 82
    reeds = 83
    jukebox = 84
    fence = 85
    pumpkin = 86
    netherrack = 87
    soul_sand = 88
    glowstone = 89
    portal = 90
    lit_pumpkin = 91
    cake = 92
    unpowered_repeater = 93
    powered_repeater = 94
    stained_glass = 95
    trapdoor = 96
    monster_egg = 97
    stonebrick = 98
    brown_mushroom_block = 99
    red_mushroom_block = 100
    iron_bars = 101
    glass_pane = 102
    melon_block = 103
    pumpkin_stem = 104
    melon_stem = 105
    vine = 106
    fence_gate = 107
    brick_stairs = 108
    stone_brick_stairs = 109
    mycelium = 110
    waterlily = 111
    nether_brick = 112
    nether_brick_fence = 113
    nether_brick_stairs = 114
    nether_wart = 115
    enchanting_table = 116
    brewing_stand = 117
    cauldron = 118
    end_portal = 119
    end_portal_frame = 120
    end_stone = 121
    dragon_egg = 122
    redstone_lamp = 123
    lit_redstone_lamp = 124
    double_wooden_slab = 125
    wooden_slab = 126
    cocoa = 127
    sandstone_stairs = 128
    emerald_ore = 129
    ender_chest = 130
    tripwire_hook = 131
    tripwire = 132
    emerald_block = 133
    spruce_stairs = 134
    birch_stairs = 135
    jungle_stairs = 136
    command_block = 137
    beacon = 138
    cobblestone_wall = 139
    flower_pot = 140
    carrots = 141
    potatoes = 142
    wooden_button = 143
    skull = 144
    anvil = 145
    trapped_chest = 146
    light_weighted_pressure_plate = 147
    heavy_weighted_pressure_plate = 148
    unpowered_comparator = 149
    powered_comparator = 150
    daylight_detector = 151
    redstone_block = 152
    quartz_ore = 153
    hopper = 154
    quartz_block = 155
    quartz_stairs = 156
    activator_rail = 157
    dropper = 158
    stained_hardened_clay = 159
    stained_glass_pane = 160
    leaves2 = 161
    log2 = 162
    acacia_stairs = 163
    dark_oak_stairs = 164
    slime = 165
    barrier = 166
    iron_trapdoor = 167
    prismarine = 168
    sea_lantern = 169
    hay_block = 170
    carpet = 171
    hardened_clay = 172
    coal_block = 173
    packed_ice = 174
    large_flowers = 175
    standing_banner = 176
    wall_banner = 177
    daylight_detector_inverted = 178
    red_sandstone = 179
    red_sandstone_stairs = 180
    double_stone_slab2 = 181
    stone_slab2 = 182
    spruce_fence_gate = 183
    birch_fence_gate = 184
    jungle_fence_gate = 185
    dark_oak_fence_gate = 186
    acacia_fence_gate = 187
    spruce_fence = 188
    birch_fence = 189
    jungle_fence = 190
    dark_oak_fence = 191
    acacia_fence = 192
    spruce_door = 193
    birch_door = 194
    jungle_door = 195
    acacia_door = 196
    dark_oak_door = 197

SubclassBlockMapping = {
}

class WoodPlank(Block):
    class PlankTypes(enum.Enum):
        oak = 0
        spruce = 1
        birch = 2
        jungle = 3
        acacia = 4
        dark_oak = 5

    def __init__(self, *args):
        super().__init__(*args)
        #self.type = PlankTypes(self.damage)

class ColoredBlock(Block):
    class ColorTypes(enum.Enum):
        white = 0
        orange = 1
        magenta = 2
        light_blue = 3
        yellow = 4
        lime = 5
        pink = 6
        gray = 7
        light_gray = 8
        cyan = 9
        purple = 10
        blue = 11
        brown = 12
        green = 13
        red = 14
        black = 15

    def __init__(*args):
        super().__init__(*args)
        self.color = ColorTypes(self.damage)
