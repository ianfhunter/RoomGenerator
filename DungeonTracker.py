from RoomGenerator.main import RoomFactory, Cell
from RoomGenerator.AssetManager import PlayerIconManager
import xlsxwriter


PIM = PlayerIconManager()

class Player():
    def __init__(self, ID, icon):
        self.ID = ID
        self.coords = None
        self.icon = icon


class DungeonTracker():
    def __init__(self):
        self.players = []

        self.current_room = self.nextRoom()

    def nextRoom(self):
        if not hasattr(self, "current_room"):
            # There was no previous room.
            self.room_factory = RoomFactory()
            room = self.room_factory.create_room()
        else:
            room = self.room_factory.create_room()

        # Populate Room
        for p in self.players:
            p.coords = self.room_factory.insert_thing_randomly(room, Cell.Type.PLAYER , thing_ID=p.ID)

        self.current_room = room
        return room

    def add_player(self, ID, icon="1"):
        print("Add Player: ", ID)
        already_exists = False
        for p in self.players:
            if ID == p.ID:
                already_exists = True
        if not already_exists:
            p = Player(ID, icon)
            self.players.append(p)
            self.room_factory.insert_thing_randomly(self.current_room, Cell.Type.PLAYER, thing_ID=ID)

    def movePlayer(self, ID, location):
        ID = str(ID)
        location = location.strip(" ").upper()
        try:
            location = list(xlsxwriter.utility.xl_cell_to_rowcol(location))
        except AttributeError:
            # Backwards, silly users.
            location = list(xlsxwriter.utility.xl_cell_to_rowcol(location[::-1]))

        location = location[::-1]
        location[1] += 1

        for p in self.players:
            print(ID, "==", p.ID)
            if ID == str(p.ID):            
                pass_status, msg = self.room_factory.move_thing(self.current_room, ID, location)       
                return pass_status, msg

        return (False, "player not found")


    def draw(self):
        return self.current_room.show(gui="img")

    def describe(self):
        return self.current_room.show(gui="describe")

    def debug(self):
        return self.current_room.show(gui="cmd")

    def get_player(self, which):
        for p in self.players:
            if (p.ID == which):
                return p
        return False