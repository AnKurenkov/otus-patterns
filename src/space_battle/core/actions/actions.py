from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.base import Fuelable, Movable, Rotatable
from src.space_battle.core.exceptions.exceptions import NotEnoughFuelError


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


class CheckFuel(ActionBase):
    def __init__(self, f: Fuelable):
        self._f = f

    def execute(self):
        if self._f.fuel < self._f.fuel_consumption:
            raise NotEnoughFuelError(
                f"Недостаточно топлива у объекта. Текущий уровень: {self._f.fuel}, "
                f"расход: {self._f.fuel_consumption}."
            )


class BurnFuel(ActionBase):
    def __init__(self, f: Fuelable):
        self._f = f

    def execute(self):
        self._f.fuel = max(self._f.fuel - self._f.fuel_consumption, 0)


class ChangeVelocity(ActionBase):
    def __init__(self, mr: Movable | Rotatable):
        self._mr = mr

    def execute(self):
        if isinstance(self._mr, Movable) and isinstance(self._mr, Rotatable):
            self._mr.velocity.set_angle_by_direction(self._mr.direction)
