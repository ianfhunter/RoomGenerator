from random import randint, choice
import numpy as np
from enum import Enum, auto
from PIL import Image, ImageDraw
import sys
import os
import tracery
import pathlib

class Cell():
    class Type(Enum):
        EMPTY = auto()
        WALL = auto()
        DOOR = auto()
        PORTAL = auto()
        FIRE = auto()
        PLAYER_ARCHER = auto()
        PLAYER_FIGHTER = auto()
        PLAYER_MAGE = auto()
        PLAYER_CLERIC = auto()
        PLAYER_DRUID = auto()
        PLAYER_BMAGE = auto()
        PLAYER_PALADIN = auto()

    def __init__(self):
        self.repr = " "
        self.type = Cell.Type.EMPTY
        self.contents = []

    def setType(self, t):
        type_repr_map = {
            Cell.Type.EMPTY: " ",
            Cell.Type.WALL: "#",
            Cell.Type.DOOR: "▤",
            Cell.Type.PORTAL: "🌀",
            Cell.Type.FIRE: "🔥",
            Cell.Type.PLAYER_ARCHER: "A",
            Cell.Type.PLAYER_FIGHTER: "F",
            Cell.Type.PLAYER_MAGE: "W",
            Cell.Type.PLAYER_CLERIC: "C",
            Cell.Type.PLAYER_DRUID: "D",
            Cell.Type.PLAYER_BMAGE: "B",
            Cell.Type.PLAYER_PALADIN: "P"
        }
        self.type = t
        self.repr = type_repr_map[t]

    def setContents(self, obj):
        self.contents = [obj]

class Room():
    def __init__(self, len_x, len_y):
        self.x_bounds = (0, len_x - 1)
        self.y_bounds = (0, len_y - 1)
        self.grid = np.empty((len_y, len_x), dtype=object)
        self.grid = np.array([[Cell() for _ in range(len_x)] for _ in range(len_y)])

        # Populate Border
        for x in range(len_x):
            self.grid[0][x].setType(Cell.Type.WALL)
            self.grid[len_y - 1][x].setType(Cell.Type.WALL)

        for y in range(len_y):
            self.grid[y][0].setType(Cell.Type.WALL)
            self.grid[y][len_x - 1].setType(Cell.Type.WALL)

    def show(self, gui="cmd"):
        print("Room Size:", self.grid.shape)
        if gui == "cmd":
            for y in range(len(self.grid)):
                for x in range(len(self.grid[0])):
                    print(self.grid[y][x].repr, end="")
                print("")
            print("")
        elif gui == "img":
            i = ImageMaker()
            i.create_base(self.grid.shape)
            for y in range(len(self.grid)):
                for x in range(len(self.grid[0])):
                    i.paintTile(self.grid[y][x].type, y, x)
            return i.save()
        elif gui == "describe":

            wall_count = str(4)
            room_rules = {
                'room':"The room consists of "+wall_count+ " walls #wall_detail#. #wall_decor#.",
                'wall_detail': [
                    "made of solid stone", 
                    "that are crumbling from old age",
                    "overgrown with vines",
                    "perfectly tiled with old grey stone slabs"
                ],
                'wall_decor': [
                    "On one of the walls #wall_hanging#",
                    "On the ground #floor_decor#"
                ],
                "wall_hanging": [
#                    "are several scones, illuminating the room"    #TODO: Lighting
                    "is a torn tapestry telling a story of #legend#",
                    "an engraving depicting #legend#",
                    "a shattered mirror hangs by the thinnest of strings"
                ],
                "legend":[
                    "great warriors fighting a terrible evil",
                    "a snake with seven heads",
                    "a dragon eating terrified villagers",
                    "women sacrificing children to a fiend"
                ],
                "floor_decor": [
                    "dust piles up in heaps",
                    "dried blood stains indicate signs of a long-forgotten battle",
                    "stray bones crack underfoot"
                ]
            }
            grammar = tracery.Grammar(room_rules)
            description = grammar.flatten("#room#")


            contents = {}
            for y in range(len(self.grid)):
                for x in range(len(self.grid[0])):
                    t = self.grid[y][x].type
                    if t in contents:
                        contents[t] += 1
                    else:
                        contents[t] = 1
            for x in contents:
                if x in [Cell.Type.FIRE]:
                    fire_rules = {
                        'fire':"#fire2#",
                        "fire2":[
                            "You feel the heat of a fire.",
                            "A fire gives the room a pleasant glow."
                        ]
                    }
                    grammar = tracery.Grammar(fire_rules)
                    description += grammar.flatten("#fire#")
                if x in [Cell.Type.DOOR]:
                    if contents[x] > 1:
                        description += "\n There are "+str(contents[x])+" doors."
                    else:
                        description += "\n There is only one door."

            return description

        else:
            raise NotImplementedError



    def insert(self, item, at_y, at_x, obj=None):
        self.grid[at_y][at_x].setType(item)
        if obj is not None:
            self.grid[at_y][at_x].setContents(obj)


class RoomFactory():
    def __init__(self):
        pass

    def insert_door(self, room):
        which_wall = choice(["N", "S", "W", "E"])
        lookup = {
            "N": (None, 0),
            "S": (None, room.y_bounds[1]),
            "W": (0, None),
            "E": (room.x_bounds[1], None)
        }

        orientation = lookup[which_wall]
        chosen_x = orientation[0] if isinstance(orientation[0], int) else randint(room.x_bounds[0]+1, room.x_bounds[1]-1 )
        chosen_y = orientation[1] if isinstance(orientation[1], int) else randint(room.y_bounds[0]+1, room.y_bounds[1]-1 )

        room.insert(Cell.Type.DOOR, chosen_y, chosen_x)

    def insert_thing(self, room, thing):
        x = randint(room.x_bounds[0]+1, room.x_bounds[1]-1)
        y = randint(room.y_bounds[0]+1, room.y_bounds[1]-1)
        room.grid[y][x].setType(thing)

    def create_room(self):
        r = Room(randint(3, 15), randint(3, 10))
        self.insert_door(r)
        self.insert_thing(r, Cell.Type.FIRE)
        return r

    def add_player(self, config, room):
        self.insert_thing(room, Cell.Type.PLAYER)

class ImageMaker():
    def __init__(self):
        resources = os.path.join(pathlib.Path(__file__).parent.absolute(), "../Resources/Tiles/")
        self.tile_sets = {
            "dungeon": {
                "file": Image.open(os.path.join(resources, "wee_dungeon.png"), "r"),
                "initial_offset": (10, 10),
                "spacing": (10, 10)
            },
            "monster": {
                "file": Image.open(os.path.join(resources, "wee_monsters.png"), "r"),
                "initial_offset": (25,4),
                "spacing": (10, 10)
            }
        }
        self.tile_size = (10, 10)
        self.scaling_method = Image.NEAREST
        self.animation_frames = 2
        self.animation_length = 300  # ms

    def create_base(self, shape):
        size = (shape[0] * self.tile_size[0], shape[1] * self.tile_size[1])
        self.canvas = [Image.new("RGBA", size, (56, 56, 56, 255)) for _ in range(self.animation_frames)]
        self.canvas[0].save("background.png")

    def paintTile(self, cell_type, y, x):
        display_lookup = {
            Cell.Type.EMPTY: ("dungeon", [(4, 0), (4, 0)]),
            Cell.Type.WALL: ("dungeon", [(0, 0), (0, 0)]),
            Cell.Type.DOOR: ("dungeon", [(0, 1), (0, 1)]),
            Cell.Type.PORTAL: ("dungeon", [(6, 4), (6, 4)]),
            Cell.Type.FIRE: ("dungeon", [(5, 2), (5, 3)]),
            Cell.Type.PLAYER_ARCHER: ("monster", [(1, 0), (1, 4)]),
            Cell.Type.PLAYER_FIGHTER: ("monster", [(0, 0), (0, 4)]),
            Cell.Type.PLAYER_MAGE: ("monster", [(2, 0), (2, 4)]),
            Cell.Type.PLAYER_CLERIC: ("monster", [(3, 0), (3, 4)]),
            Cell.Type.PLAYER_DRUID: ("monster", [(4, 0), (4, 4)]),
            Cell.Type.PLAYER_BMAGE: ("monster", [(5, 0), (5, 4)]),
            Cell.Type.PLAYER_PALADIN: ("monster", [(6, 0), (6, 4)]),
        }
        tile = display_lookup[cell_type]

        for canvas_idx, t in enumerate(tile[1]):
            tileset = self.tile_sets[tile[0]]
            offset = tileset["initial_offset"]
            tile_file = tileset["file"]
            spacing = tileset["spacing"]

            # Get Tile
            y_begin = offset[0] + t[0] * (self.tile_size[0] + spacing[0])
            y_end = y_begin + self.tile_size[0]

            x_begin = offset[1] + t[1] * (self.tile_size[1] + spacing[1])
            x_end = x_begin + self.tile_size[1]

            tile_area = (x_begin, y_begin, x_end, y_end)
            cropped_t = tile_file.crop(tile_area)

            # Place
            where = (y * self.tile_size[0], x * self.tile_size[1])

            self.canvas[canvas_idx].paste(cropped_t, where, cropped_t)


    def prepare_for_screen(self, resize=True):
        scale_width = 10
        scale_height = 10
        upscaled_canvas = []
        for f in range(self.animation_frames):
            new_size = (self.canvas[f].size[0] * scale_height, self.canvas[f].size[1] * scale_width)
            upscaled_canvas.append(self.canvas[f].resize(new_size, self.scaling_method))
        return upscaled_canvas

    def save(self):
        canvases = self.prepare_for_screen()
        filename = "TestImage" + str(randint(0, 10000)) + ".gif"
        canvases[0].save(
            filename,
            format="GIF",
            append_images=[c for c in canvases[1:]],
            save_all=True,
            duration=self.animation_length,
            loop=0,
        )
        return filename



if __name__ == "__main__":
    gui="cmd"
    gui="img"

    for _ in range(5):
        rf = RoomFactory()
        r = rf.create_room()
        r.show(gui=gui)
