import pytest

from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.fuelable_adapter_actions import IocRegisterFuelableAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities.fuelable import Fuelable
from src.space_battle.core.objects.game_object_base import GameObjectBase


class TestFuelableAdapterActions:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        IocRegisterFuelableAction().execute()
        IocRegisterCreateAdapterAction().execute()

    @staticmethod
    def test_fuel_set_get():
        obj = GameObjectBase("obj1", "test", {"Fuelable"})
        adapter = Ioc.resolve("Adapter", Fuelable, Fuelable, obj)

        adapter.fuel = 42

        assert adapter.fuel == 42
        assert obj.get_property("fuel") == 42

    @staticmethod
    def test_fuel_consumption_set_get():
        obj = GameObjectBase("obj1", "test", {"Fuelable"})
        adapter = Ioc.resolve("Adapter", Fuelable, Fuelable, obj)

        adapter.fuel_consumption = 7

        assert adapter.fuel_consumption == 7
        assert obj.get_property("fuel_consumption") == 7
