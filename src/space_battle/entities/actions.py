from src.space_battle.core.base import Movable


class Move:
    def __init__(self, m: Movable):
        self._m = m

    def execute(self):
        self._m.location = self._m.location.move_to(self._m.velocity)
