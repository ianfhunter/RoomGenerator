from random import randint, choice
import numpy as np
from enum import Enum, auto
from PIL import Image, ImageDraw
import sys, os

class Cell():
    class Type(Enum):
        EMPTY = auto()
        WALL = auto()
        DOOR = auto()
        PORTAL = auto()
        FIRE = auto()
        PLAYER = auto()

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
            Cell.Type.PLAYER: "@"
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
            i.save()
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
        self.insert_thing(r, Cell.Type.PLAYER)
        return r

class ImageMaker():
    def __init__(self):
        self.tile_sets = {
            "dungeon": {
                "file": Image.open("wee_dungeon.png", "r"),
                "initial_offset": (10, 10),
                "spacing": (10, 10)
            },
            "monster": {
                "file": Image.open("wee_monsters.png", "r"),
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
            Cell.Type.PLAYER: ("monster", [(1, 0), (1, 4)]),
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
        print(canvases)
        canvases[0].save(
            "TestImage" + str(randint(0, 10000)) + ".gif",
            format="GIF",
            append_images=[c for c in canvases[1:]],
            save_all=True,
            duration=self.animation_length,
            loop=0,
        )



if __name__ == "__main__":
    gui="cmd"
    gui="img"

    for _ in range(5):
        rf = RoomFactory()
        r = rf.create_room()
        r.show(gui=gui)
