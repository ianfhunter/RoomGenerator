from RoomGenerator.main import RoomFactory, Cell

class Player():
    def __init__(self, ID, icon):
        self.ID = ID
        self.coords = None
        self.choose_icon(icon)

    def choose_icon(self, icon):

        choices = {
            "1": Cell.Type.PLAYER_FIGHTER,
            "2": Cell.Type.PLAYER_ARCHER,
            "3": Cell.Type.PLAYER_MAGE,
            "4": Cell.Type.PLAYER_CLERIC,
            "5": Cell.Type.PLAYER_DRUID,
            "6": Cell.Type.PLAYER_BMAGE,
            "7": Cell.Type.PLAYER_PALADIN
        }

        self.icon = choices[str(icon)]

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
            p.coords = self.room_factory.insert_thing(room, p.icon)

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
            self.room_factory.insert_thing(self.current_room, p.icon)

    def draw(self):
        return self.current_room.show(gui="img")

    def describe(self):
        return self.current_room.show(gui="describe")

    def get_player(self, which):
        for p in self.players:
            if (p.ID == which):
                return p
        return False