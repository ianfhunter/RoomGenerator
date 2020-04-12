import re
from enum import Enum, auto
import pathlib
import os
from PIL import Image
from RoomGenerator.Cell import Cell

class AssetManager():
    def __init__(self):
        
        # Load Tilesets
        self.asset_folder = os.path.join(pathlib.Path(__file__).parent.absolute(), "../Resources/")
        self.tile_sets = {
            "dungeon": {
                "file": Image.open(os.path.join(self.asset_folder, "Tiles/wee_dungeon.png"), "r"),
                "initial_offset": (10, 10),
                "spacing": (10, 10),
                "tile_size": (10, 10)
            },
            "monster": {
                "file": Image.open(os.path.join(self.asset_folder, "Tiles/wee_monsters.png"), "r"),
                "initial_offset": (25,4),
                "spacing": (10, 10),
                "tile_size": (10, 10)
            }
        }

class PlayerIconManager(AssetManager):
    def __init__(self):
        super().__init__()

    def parseChoice(self, string):
        return str(re.search(r'\d+', string).group())

    def getIcon(self, select):
        select = str(select)    

        choices = {
            "-1": ("monster", [(0, 0), (0, 4)]), # Default
            "1":  ("monster", [(0, 0), (0, 4)]),
            "2":  ("monster", [(1, 0), (1, 4)]),
            "3":  ("monster", [(2, 0), (2, 4)]),
            "4":  ("monster", [(3, 0), (3, 4)]),
            "5":  ("monster", [(4, 0), (4, 4)]),
            "6":  ("monster", [(5, 0), (5, 4)]),
            "7":  ("monster", [(6, 0), (6, 4)]),
        }

        icon = choices[select]
        return icon


class SceneryManager(AssetManager):

    class Scene(Enum):
        DESERT = auto()
        DUNGEON = auto()

    def __init__(self, scene=Scene.DUNGEON):
        super().__init__()

        self.scene = scene

        self.backgrounds = {
            SceneryManager.Scene.DUNGEON: (56, 56, 56, 255),
            SceneryManager.Scene.DESERT: (250, 162, 27, 255)
        }
        self.walls = {
            SceneryManager.Scene.DUNGEON: ("dungeon", [(0, 0), (0, 0)]),
            SceneryManager.Scene.DESERT: ("dungeon", [(0, 0), (0, 0)])
        }
        self.doors = {
            SceneryManager.Scene.DUNGEON: ("dungeon", [(0, 1), (0, 1)]),
            SceneryManager.Scene.DESERT: ("dungeon", [(0, 1), (0, 1)])
        }
        self.portals = ("dungeon", [(6, 4), (6, 4)])
        self.fire = ("dungeon", [(5, 2), (5, 3)])
        self.empty = ("dungeon", [(4, 0), (4, 0)])


    def get_background(self):
        return self.backgrounds[self.scene]

    def get_tile(self, cell_enum):
        lookups = {
            Cell.Type.EMPTY: self.empty,
            Cell.Type.WALL: self.walls,
            Cell.Type.DOOR: self.doors,
            Cell.Type.PORTAL: self.portals,
            Cell.Type.FIRE: self.fire,
        }

        selection = lookups[cell_enum]
        if isinstance(selection, dict):
            # choice based on scene
            return selection[self.scene]
        else:
            # only one image
            return selection

    def decorate(self, unique_id, grid):

        random.seed(unique_id)  
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                # Less efficient to have first, but more reproducable
                if random.randrange(10) == 0:   
                    if cell_enum == Cell.Type.EMPTY:
                        # potentially decorate
                        print(f"decorate cell {y},{x}")
