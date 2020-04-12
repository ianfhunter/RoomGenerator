from enum import Enum, auto

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
        self.contentID = 0

    def setType(self, t, ID=0):
        self.type = t
        self.contentID = ID

    def setContents(self, obj):
        self.contents = [obj]
