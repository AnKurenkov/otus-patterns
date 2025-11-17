from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.base import Movable, Rotatable

# TODO: перенести в core.actions??


class Move(ActionBase):
    def __init__(self, m: Movable):
        self._m = m

    def execute(self):
        self._m.location = self._m.location.move_to(self._m.velocity)


class Rotate(ActionBase):
    def __init__(self, r: Rotatable):
        self._r = r

    def execute(self):
        self._r.direction = self._r.direction.rotate_by(self._r.angular_velocity)
