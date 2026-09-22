import pytest

from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.destroyable_adapter_actions import IocRegisterDestroyableAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities.destroyable import Destroyable
from src.space_battle.core.objects.game_object_base import GameObjectBase


class TestDestroyableAdapterActions:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        IocRegisterDestroyableAction().execute()
        IocRegisterCreateAdapterAction().execute()

    @staticmethod
    def test_health_set_get():
        obj = GameObjectBase("obj1", "test", {"Destroyable"})
        adapter = Ioc.resolve("Adapter", Destroyable, Destroyable, obj)

        adapter.health = 100

        assert adapter.health == 100
        assert obj.get_property("health") == 100
