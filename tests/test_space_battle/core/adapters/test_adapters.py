import logging
from abc import ABC, abstractmethod

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.movable_adapter_actions import IocRegisterMovableAction
from src.space_battle.core.base import Movable
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.space import Point

logger = logging.getLogger(__name__)


class TestAdapters:

    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        IocRegisterMovableAction().execute()
        IocRegisterCreateAdapterAction().execute()

    @staticmethod
    def test_ioc_resolve_adapter():
        adapter = Ioc.resolve("Adapter", Movable, Movable, object())

        assert type(adapter).__name__ == "MovableAdapter"
        assert hasattr(type(adapter), "location")
        assert hasattr(type(adapter), "velocity")

    @staticmethod
    def test_adapter_with_property():
        adapter1 = Ioc.resolve("Adapter", Movable, Movable, "obj1")
        adapter2 = Ioc.resolve("Adapter", Movable, Movable, "obj2")

        adapter1.location = Point(1, 1)
        adapter2.location = Point(2, 2)

        assert adapter1.location == Point(1, 1)
        assert adapter2.location == Point(2, 2)

    @staticmethod
    def test_adapter_with_method_return_none(capsys):
        class InterfaceWithMethod(ABC):
            @abstractmethod
            def method(self): ...

            @property
            @abstractmethod
            def property(self): ...

        class InterfaceWithMethodAction(ActionBase):
            def __init__(self, obj):
                self._obj = obj

            def execute(self):
                print("Hello!!")

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "InterfaceWithMethod.method",
            lambda obj: InterfaceWithMethodAction(obj).execute(),
        ).execute()

        adapter = Ioc.resolve("Adapter", InterfaceWithMethod, InterfaceWithMethod, object())
        adapter.method()

        assert "Hello!!" in capsys.readouterr().out

    @staticmethod
    def test_adapter_with_method_return():
        class InterfaceWithMethod(ABC):
            @abstractmethod
            def method(self, num: int) -> int: ...

            @property
            @abstractmethod
            def property(self): ...

        class InterfaceWithMethodAction(ActionBase):
            def __init__(self, obj, num: int):
                self._obj = obj
                self._num = num

            def execute(self):
                return self._num

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "InterfaceWithMethod.method",
            lambda obj, *args: InterfaceWithMethodAction(obj, *args).execute(),
        ).execute()

        adapter = Ioc.resolve("Adapter", InterfaceWithMethod, InterfaceWithMethod, object())
        assert adapter.method(5) == 5
