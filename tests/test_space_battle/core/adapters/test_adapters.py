import logging
from abc import ABC, abstractmethod

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.movable_adapter_actions import IocRegisterMovableAction
from src.space_battle.core.adapters.dynamic_adapter_factory import DynamicAdapterFactory
from src.space_battle.core.exceptions.exceptions import ObjectCapabilityError
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Movable
from src.space_battle.core.objects.game_object_base import GameObjectBase
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
        obj1 = GameObjectBase("obj1", "test", {"Movable"})
        obj2 = GameObjectBase("obj2", "test", {"Movable"})
        adapter1 = Ioc.resolve("Adapter", Movable, Movable, obj1)
        adapter2 = Ioc.resolve("Adapter", Movable, Movable, obj2)

        adapter1.location = Point(1, 1)
        adapter2.location = Point(2, 2)

        assert adapter1.location == Point(1, 1)
        assert adapter2.location == Point(2, 2)
        assert obj1.get_property("location") == Point(1, 1)
        assert obj2.get_property("location") == Point(2, 2)

    @staticmethod
    def test_adapter_t1_resolve_fast_fail():
        obj = GameObjectBase("obj1", "test", {"Fuelable"})

        with pytest.raises(ObjectCapabilityError):
            Ioc.resolve("Adapter", Movable, Movable, obj)

    @staticmethod
    def test_adapter_t2_guard_on_capability_loss():
        obj = GameObjectBase("obj1", "test", {"Movable"})
        adapter = Ioc.resolve("Adapter", Movable, Movable, obj)
        adapter.location = Point(5, 5)
        assert adapter.location == Point(5, 5)

        obj.capabilities.discard("Movable")

        with pytest.raises(ObjectCapabilityError):
            _ = adapter.location
        with pytest.raises(ObjectCapabilityError):
            adapter.location = Point(9, 9)

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

    @staticmethod
    def test_create_adapter_factory_rejects_non_abc():
        with pytest.raises(ValueError):
            DynamicAdapterFactory.create_adapter_factory(int)

    @staticmethod
    def test_adapter_with_void_method_annotation():
        class InterfaceWithVoidMethod(ABC):
            @abstractmethod
            def method(self) -> None: ...

        class VoidMethodAction(ActionBase):
            executed = False

            def __init__(self, obj):
                self._obj = obj

            def execute(self):
                type(self).executed = True

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "InterfaceWithVoidMethod.method",
            lambda obj: VoidMethodAction(obj),
        ).execute()

        adapter = Ioc.resolve("Adapter", InterfaceWithVoidMethod, InterfaceWithVoidMethod, object())
        adapter.method()

        assert VoidMethodAction.executed
