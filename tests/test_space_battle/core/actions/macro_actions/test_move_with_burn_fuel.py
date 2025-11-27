import pytest

from src.space_battle.core.actions.actions import BurnFuel, CheckFuel, Move
from src.space_battle.core.actions.macro_actions import MoveWithBurnFuel
from src.space_battle.core.exceptions.exceptions import NotEnoughFuelError
from src.space_battle.core.space import CartesianVelocity, Point, PolarVelocity
from tests.test_space_battle.core import FuelableStub, MovableStub


class TestMoveWithBurnFuel:
    @staticmethod
    def test_move_with_enough_fuel():
        obj_f = FuelableStub(fuel=3, fuel_consumption=2)
        obj_m = MovableStub(Point(12, 5), PolarVelocity(7, 0))
        MoveWithBurnFuel((CheckFuel(obj_f), Move(obj_m), BurnFuel(obj_f))).execute()
        assert obj_f.fuel == 1
        assert obj_m.location == CartesianVelocity(19, 5)

    @staticmethod
    def test_move_with_not_enough_fuel():
        obj_f = FuelableStub(fuel=3, fuel_consumption=4)
        obj_m = MovableStub(Point(12, 5), PolarVelocity(7, 0))
        with pytest.raises(NotEnoughFuelError):
            MoveWithBurnFuel((CheckFuel(obj_f), Move(obj_m), BurnFuel(obj_f))).execute()
