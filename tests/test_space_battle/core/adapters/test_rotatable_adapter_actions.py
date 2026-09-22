import pytest

from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.rotatable_adapter_actions import IocRegisterRotatableAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities.rotatable import Rotatable
from src.space_battle.core.objects.game_object_base import GameObjectBase
from src.space_battle.core.space import Direction


class TestRotatableAdapterActions:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        IocRegisterRotatableAction().execute()
        IocRegisterCreateAdapterAction().execute()

    @staticmethod
    def test_direction_set_get():
        obj = GameObjectBase("obj1", "test", {"Rotatable"})
        adapter = Ioc.resolve("Adapter", Rotatable, Rotatable, obj)

        adapter.direction = Direction(3, 8)

        assert adapter.direction.d == 3
        assert adapter.direction.n == 8
        assert obj.get_property("direction") == Direction(3, 8)

    @staticmethod
    def test_angular_velocity_set_get():
        obj = GameObjectBase("obj1", "test", {"Rotatable"})
        adapter = Ioc.resolve("Adapter", Rotatable, Rotatable, obj)

        adapter.angular_velocity = 2

        assert adapter.angular_velocity == 2
        assert obj.get_property("angular_velocity") == 2
