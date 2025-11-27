from src.space_battle.core.base import Fuelable, Movable, Rotatable
from src.space_battle.core.space import Direction, Point, PolarVelocity


class MovableStub(Movable):
    def __init__(self, location: Point, velocity: PolarVelocity):
        self._location = location
        self._velocity = velocity

    @property
    def location(self) -> Point:
        return self._location

    @location.setter
    def location(self, location: Point):
        self._location = location

    @property
    def velocity(self) -> PolarVelocity:
        return self._velocity


class RotatableStub(Rotatable):
    def __init__(self, direction: Direction, angular_velocity: int):
        self._direction = direction
        self._angular_velocity = angular_velocity

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction):
        self._direction = direction

    @property
    def angular_velocity(self) -> int:
        return self._angular_velocity


class FuelableStub(Fuelable):
    def __init__(self, fuel: int, fuel_consumption: int):
        self._fuel = fuel
        self._fuel_consumption = fuel_consumption

    @property
    def fuel(self) -> int:
        return self._fuel

    @fuel.setter
    def fuel(self, fuel: int):
        self._fuel = fuel

    @property
    def fuel_consumption(self) -> int:
        return self._fuel_consumption
