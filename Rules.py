from enum import Enum, auto
class Rules():

    class MovementRule(Enum):
        SQUARE = auto()  # Limit X and Y seperately
        DIAMOND = auto()  # Limit combined X and Y
        CIRCLE = auto()  # Use Pi and shit.

    """
        e.g.
        SQUARE:
         |X|X|X|X|X|X|
         |X|X|X|X|X|X|
         |X|X|X|X|X|X|
         |X|X|X|X|X|X|
         |X|X|X|X|X|X|
         |O|X|X|X|X|X|
        DIAMOND:
         |X| | | | | |
         |X|X| | | | |
         |X|X|X| | | |
         |X|X|X|X| | |
         |X|X|X|X|X| |
         |O|X|X|X|X|X|
        CIRCLE:
         |X| | | | | |
         |X|X|X| | | |
         |X|X|X|X| | |
         |X|X|X|X|X| |
         |X|X|X|X|X| |
         |O|X|X|X|X|X|

         TODO: Figure out how to do circle.
         Maybe https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    """

    def __init__(self):
        self.max_movement = 6
        self.movement_rule = Rules.MovementRule.SQUARE

    def movementPermitted(self, from_yx, to_yx):
        if self.movement_rule == Rules.MovementRule.SQUARE:
            if abs(from_yx[0] - to_yx[0]) > self.max_movement:
                return False
            if abs(from_yx[1] - to_yx[1]) > self.max_movement:
                return False
            return True
        elif self.movement_rule == Rules.MovementRule.DIAMOND:
            y_movement = abs(from_yx[0] - to_yx[0])
            x_movement = abs(from_yx[1] - to_yx[1])
            if y_movement + x_movement > self.max_movement:
                return False
            return True
        else:
            raise NotImplementedError
