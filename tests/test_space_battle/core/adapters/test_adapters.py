from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.movable_adapter_actions import IocRegisterMovableAction
from src.space_battle.core.base import Movable
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction
from src.space_battle.core.space import Point


class TestAdapters:

    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        InitAction().execute()
        ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()
        IocRegisterMovableAction().execute()
        IocRegisterCreateAdapterAction().execute()
        yield
        Ioc.resolve("IoC.Scope.Current.Clear", ActionBase).execute()

    def test_ioc_resolve_adapter(self):
        adapter = Ioc.resolve("Adapter", Movable, Movable, object())

        assert type(adapter).__name__ == "MovableAdapter"
        assert hasattr(type(adapter), "location")
        assert hasattr(type(adapter), "velocity")

    def test_using_adapter(self):
        adapter1 = Ioc.resolve("Adapter", Movable, Movable, "obj1")
        adapter2 = Ioc.resolve("Adapter", Movable, Movable, "obj2")

        adapter1.location = Point(1, 1)
        adapter2.location = Point(2, 2)

        assert adapter1.location == Point(1, 1)
        assert adapter2.location == Point(2, 2)
