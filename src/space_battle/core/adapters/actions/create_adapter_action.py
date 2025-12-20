from typing import Type, TypeVar, cast

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.adapters.dynamic_adapter_factory import AdapterFactoryBase, DynamicAdapterFactory
from src.space_battle.core.ioc import Ioc

T = TypeVar("T")


class IocRegisterCreateAdapterAction(ActionBase):
    def execute(self):
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Adapter",
            lambda interface_type, obj: CreateAdapterAction(interface_type, obj).execute(),
        ).execute()


class CreateAdapterAction(ActionBase):
    def __init__(self, interface_type: Type[T], obj):
        self._interface_type = interface_type
        self._obj = obj

    def execute(self) -> T:
        factory: AdapterFactoryBase[T] = DynamicAdapterFactory.create_adapter_factory(self._interface_type)
        return cast(T, factory.create(self._obj))
