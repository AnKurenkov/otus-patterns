from typing import Type, TypeVar, cast

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.adapters.dynamic_adapter_factory import AdapterFactoryBase, DynamicAdapterFactory
from src.space_battle.core.exceptions.exceptions import ObjectCapabilityError
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
        self._check_capability()
        factory: AdapterFactoryBase[T] = DynamicAdapterFactory.create_adapter_factory(self._interface_type)
        return cast(T, factory.create(self._obj))

    def _check_capability(self):
        capabilities = getattr(self._obj, "capabilities", None)
        if capabilities is not None and self._interface_type.__name__ not in capabilities:
            raise ObjectCapabilityError(
                f"Объект {self._obj} не поддерживает способность '{self._interface_type.__name__}'."
                f"Текущие способности: {capabilities}"
            )
