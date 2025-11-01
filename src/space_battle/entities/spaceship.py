from space_battle.core.space import Direction, Point, VectorBase
from src.space_battle.core.base import Movable, Rotatable


class Spaceship(Movable, Rotatable):
    """Корабль, который может: двигаться, вращаться"""

    def __init__(self, location: Point, velocity: VectorBase, direction: Direction, angular_velocity: int):
        self._location = location
        self._velocity = velocity
        self._direction = direction
        self._angular_velocity = angular_velocity

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

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction):
        self._direction = direction

    @property
    def angular_velocity(self) -> int:
        return self._angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, angular_velocity: int):
        self._angular_velocity = angular_velocity
