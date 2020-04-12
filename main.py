from random import randint, choice
import numpy as np
import sys
import os
import xlsxwriter
import random
import tracery
import pathlib

from RoomGenerator.Cell import Cell
from RoomGenerator.Rules import Rules
from RoomGenerator.Display import ImageMaker

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
                    i.paintTile(self.grid[y][x], y, x)
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



    def insert(self, item, at_y, at_x, obj=None, ID=0):
        self.grid[at_y][at_x].setType(item, ID=ID)
        if obj is not None:
            self.grid[at_y][at_x].setContents(obj)

    def removeObjectByID(self, ID):
        popped = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if ID == self.grid[y][x].contentID:
                    popped.append((self.grid[y][x], y, x))
                    self.grid[y][x] = Cell()

        if len(popped) == 0:
            print(f"ID '{ID}' not found.")
        return popped

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


    def insert_thing(self, room, thing_icon, thing_ID, where_y, where_x):
        room.insert(thing_icon, where_y, where_x, ID=thing_ID)
        return where_y, where_x

    def insert_thing_randomly(self, room, thing_icon, thing_ID=0, solid=True):
        chosen_x = randint(room.x_bounds[0]+1, room.x_bounds[1]-1)
        chosen_y = randint(room.y_bounds[0]+1, room.y_bounds[1]-1)
        return self.insert_thing(room, thing_icon, thing_ID, chosen_y, chosen_x)

    def move_thing(self, room, ID, location):

        if location[1] <= room.x_bounds[0] or location[1] >= room.x_bounds[1]:
            return False, "Something is blocking you (Y)"
        if location[0] <= room.y_bounds[0] or location[0] >= room.y_bounds[1]:
            return False, "Something is blocking you (X)"
        objs = room.removeObjectByID(ID)
        if(len(objs) != 1):
            return False, "Object Not Found"
        obj = objs[0]

        rules = Rules()
        if not rules.movementPermitted(obj[1:], location):
            # reset
            self.insert_thing(room, obj[0].type, obj[0].contentID, obj[1], obj[2])
            return False, "Movement not allowed by rules" 

        # print(obj[1], obj[2], "->", location[0], location[1])
        self.insert_thing(room, obj[0].type, obj[0].contentID, location[0], location[1])
        return True, ""

    def create_room(self):
        r = Room(randint(3, 20), randint(3, 15))
        # r = Room(randint(20, 30), randint(20, 30))
        self.insert_door(r)
        self.insert_thing_randomly(r, Cell.Type.FIRE)
        return r



if __name__ == "__main__":
    gui="cmd"
    gui="img"

    for _ in range(5):
        rf = RoomFactory()
        r = rf.create_room()
        r.show(gui=gui)
