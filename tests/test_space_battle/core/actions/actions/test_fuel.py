from unittest.mock import MagicMock, PropertyMock

import pytest

from src.space_battle.core.actions.actions import BurnFuel, CheckFuel
from src.space_battle.core.base import Fuelable
from src.space_battle.core.exceptions.exceptions import NotEnoughFuelError
from tests.test_space_battle.core import FuelableStub


@pytest.fixture
def mock_fuelable():
    def f(fuel: int, fuel_consumption: int):
        mock = MagicMock(Fuelable)
        type(mock).fuel = PropertyMock(return_value=fuel)
        type(mock).fuel_consumption = PropertyMock(return_value=fuel_consumption)
        return mock

    return f


class TestCheckFuel:
    @staticmethod
    def test_not_enough_fuel_error(mock_fuelable):
        obj_ = mock_fuelable(fuel=1, fuel_consumption=2)
        with pytest.raises(NotEnoughFuelError):
            CheckFuel(obj_).execute()

    @staticmethod
    def test_enough_fuel(mock_fuelable):
        obj_ = mock_fuelable(fuel=3, fuel_consumption=2)
        CheckFuel(obj_).execute()


class TestBurnFuel:
    @staticmethod
    def test_burn_fuel():
        obj_ = FuelableStub(fuel=3, fuel_consumption=2)
        BurnFuel(obj_).execute()
        assert obj_.fuel == 1

    @staticmethod
    def test_overburn_fuel():
        obj_ = FuelableStub(fuel=3, fuel_consumption=4)
        BurnFuel(obj_).execute()
        assert obj_.fuel == 0
