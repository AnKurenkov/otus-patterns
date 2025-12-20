from abc import ABC
from typing import Any, Protocol, Type, TypeVar, get_type_hints

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.base import Movable
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction
from src.space_battle.core.space import Point

T = TypeVar("T")


# ===== Интерфейс фабрики адаптеров =====
# class AdapterFactoryBase(ABC):
#     @abstractmethod
#     def create(self, obj: Any) -> T:
#         pass


# ===== Интерфейс фабрики адаптеров =====
class AdapterFactoryBase(Protocol[T]):
    def create(self, obj: Any) -> T: ...


# ===== Фабрика динамических адаптеров (генератор кода) =====
class DynamicAdapterFactory:
    """
    Компилирует адаптер <InterfaceName>Adapter и фабрику <InterfaceName>AdapterFactory,
    возвращает экземпляр фабрики как AdapterFactoryBase[T].
    """

    @staticmethod
    def create_adapter_factory(interface_type: Type[T]) -> AdapterFactoryBase[T]:
        """Реализация без генерации кода, с использованием метаклассов"""

        # if not isinstance(interface_type, type) and ABC not in interface_type.__bases__:
        if ABC not in interface_type.__bases__:
            raise ValueError("interface_type должен быть абстрактным классом ABC")

        adapter_class = DynamicAdapterFactory._generate_adapter_class(interface_type)
        factory_class = DynamicAdapterFactory._generate_factory_class(adapter_class, interface_type)

        return factory_class()

    @staticmethod
    def _generate_adapter_class(interface_type: Type[T]) -> type:
        """Генерирует класс адаптера динамически."""
        interface_name = interface_type.__name__  # "ActionBase"
        class_name = interface_name.removesuffix("Base") + "Adapter"  # ActionBase -> ActionAdapter

        # Собираем атрибуты (свойства) из интерфейса
        # Для ABC с @property и @abstractmethod
        adapter_attrs = {"_obj": None}  # Поле для хранения адаптируемого объекта

        def init(self, obj):
            self._obj = obj

        adapter_attrs["__init__"] = init

        # Обработка методов
        if hasattr(interface_type, "__abstractmethods__"):
            interface_type.__abstractmethods__
        else:
            pass

        # Обработка свойств
        all_properties = {}
        for cls in interface_type.__mro__:
            if cls is object:
                continue
            for name, obj_ in cls.__dict__.items():
                if isinstance(obj_, property):
                    all_properties[name] = obj_

        for prop_name, prop_descriptor in all_properties.items():
            prop_type = object
            if hasattr(prop_descriptor, "fget"):
                prop_type = get_type_hints(prop_descriptor.fget).get("return")

            setter_func = prop_descriptor.fset

            def make_getter(prop_name_, prop_type_, interface_name_):
                def getter(self):
                    dependency = f"{interface_name_}.{prop_name_}.Get"
                    return Ioc.resolve(dependency, prop_type_, self)

                return getter

            def make_setter(prop_name_, interface_name_):
                def setter(self, value):
                    dependency = f"{interface_name_}.{prop_name_}.Set"
                    Ioc.resolve(dependency, ActionBase, self, value).execute()

                return setter

            prop_getter = make_getter(prop_name, prop_type, interface_name)
            prop_setter = None
            if setter_func:
                prop_setter = make_setter(prop_name, interface_name)

            adapter_attrs[prop_name] = property(prop_getter, prop_setter)

        adapter_class = type(class_name, (interface_type,), adapter_attrs)
        return adapter_class

    @staticmethod
    def _generate_factory_class(adapter_class: type, interface_type: Type[T]) -> type:
        """Генерирует класс фабрики динамически."""

        class GeneratedFactory:
            def create(self, obj: Any) -> interface_type:
                return adapter_class(obj)

        GeneratedFactory.__name__ = adapter_class.__name__ + "Factory"
        return GeneratedFactory


# ===== Демонстрация =====
def main():
    from space_battle.core.adapters.actions.movable_adapter_actions import (
        MovableLocationGetAction,
        MovableLocationSetAction,
    )

    # Инициализируем IoC
    InitAction().execute()
    Ioc.resolve(
        "IoC.Register", ActionBase, "Movable.location.Get", lambda obj: MovableLocationGetAction(obj).execute()
    ).execute()
    Ioc.resolve(
        "IoC.Register",
        ActionBase,
        "Movable.location.Set",
        lambda obj, location: MovableLocationSetAction(obj, location),
    ).execute()

    # Строим фабрику для IMovingObject (реально создаётся MovingObjectAdapterFactory)
    factory: AdapterFactoryBase[Movable] = DynamicAdapterFactory.create_adapter_factory(Movable)

    # Дальше фабрику можно переиспользовать без рефлексии:
    obj1 = factory.create(object())
    obj2 = factory.create(object())

    print("=== USING GENERATED ADAPTERS ===")
    obj1.location = Point(x=100, y=200)
    obj2.location = Point(x=300, y=400)
    loc1 = obj1.location
    loc2 = obj2.location
    print(f"Location: {loc1.x}, {loc1.y}")
    print(f"Location: {loc2.x}, {loc2.y}")
    # vel1 = obj1.velocity
    # print(f"Velocity: {vel1.x}, {vel1.y}")

    # ----------------------------------

    from abc import ABC, abstractmethod

    class InterfaceWithMethod(ABC):
        @abstractmethod
        def method(self): ...

    DynamicAdapterFactory.create_adapter_factory(InterfaceWithMethod)


if __name__ == "__main__":
    main()
