from space_battle.core.space import Point, VectorBase
from src.space_battle.core.base import Movable


class Spaceship(Movable):
    """Корабль, который может: двигаться"""

    def __init__(self, location: Point, velocity: VectorBase):
        self._location = location
        self._velocity = velocity

    @property
    def location(self) -> Point:
        return self._location

    @location.setter
    def location(self, location: Point):
        self._location = location

    @property
    def velocity(self) -> VectorBase:
        return self._velocity

    @velocity.setter
    def velocity(self, velocity: VectorBase):
        self._velocity = velocity
