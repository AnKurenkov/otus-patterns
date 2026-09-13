from typing import Any, Optional, Set


class GameObjectBase:
    """Базовый игровой объект: данные без поведения.

    Способности (capabilities) описывают, к каким интерфейсам (Movable, Rotatable,
    Fuelable) можно адаптировать объект. Все свойства хранятся в едином
    PropertyBag (_properties) и читаются/пишутся через get_property/set_property.
    Объект не знает о конкретных свойствах своих способностей заранее —
    они появляются динамически при первом обращении через адаптеры.
    """

    def __init__(self, obj_id: str, type_name: str, capabilities: Optional[Set[str]] = None):
        self._id = obj_id
        self._type = type_name
        self._capabilities: Set[str] = set(capabilities) if capabilities else set()
        self._properties: dict = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @property
    def capabilities(self) -> Set[str]:
        return self._capabilities

    def get_property(self, name: str) -> Any:
        return self._properties[name]

    def set_property(self, name: str, value: Any):
        self._properties[name] = value

    def __repr__(self):
        return f"{self.__class__.__name__}(id: {self._id!r}, type: {self._type!r})"
