from typing import Iterable, Type, cast

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.init.game_init_exception import GameInitError
from src.space_battle.core.init.game_init_value_parser import parse_value
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities.destroyable import Destroyable
from src.space_battle.core.objects.capabilities.fuelable import Fuelable
from src.space_battle.core.objects.capabilities.movable import Movable
from src.space_battle.core.objects.capabilities.rotatable import Rotatable
from src.space_battle.core.objects.game_object_base import GameObjectBase

_SUPPORTED_VERSION = 1

_INTERFACES: dict[str, Type] = {
    "Movable": Movable,
    "Rotatable": Rotatable,
    "Fuelable": Fuelable,
    "Destroyable": Destroyable,
}


class GameInitInterpreter:
    """Интерпретатор данных initial (data-driven + IoC-фабрики объектов).

    Создаёт игровые объекты заданных типов через фабрики "Game.Init.Object.<type>",
    задаёт их свойства через адаптеры ("<Интерфейс>.<свойство>") и регистрирует
    объекты в реестре "Game.Objects".
    """

    def interpret(self, initial: dict | None):
        if initial is None:
            return
        self._validate(initial)
        self._init_field(initial.get("field"))
        for spec in initial.get("objects", []):
            self._create_object(spec)

    @staticmethod
    def _validate(initial: dict):
        version = initial.get("version")
        if version is not None and version != _SUPPORTED_VERSION:
            raise GameInitError(f"Неподдерживаемая версия initial: {version}. Ожидается {_SUPPORTED_VERSION}.")
        if not initial.get("id"):
            raise GameInitError("В initial должен быть задан 'id' игры.")

        objects = initial.get("objects")
        if objects is not None and not isinstance(objects, list):
            raise GameInitError("В initial 'objects' должен быть списком.")

        seen_ids = set()
        for spec in objects or []:
            if not isinstance(spec, dict):
                raise GameInitError(f"Описание объекта должно быть словарём, получено: {spec!r}")
            obj_id = spec.get("id")
            if not obj_id:
                raise GameInitError(f"У объекта отсутствует 'id': {spec!r}")
            if obj_id in seen_ids:
                raise GameInitError(f"Дубликат 'id' объекта: {obj_id}")
            seen_ids.add(obj_id)
            if not spec.get("type"):
                raise GameInitError(f"У объекта '{obj_id}' отсутствует 'type'.")

    @staticmethod
    def _init_field(field):
        if field is None:
            return
        if not isinstance(field, dict):
            raise GameInitError(f"'field' должен быть словарём, получено: {field!r}")
        Ioc.resolve("IoC.Register", ActionBase, "Game.Field", lambda f=field: f).execute()

    def _create_object(self, spec: dict):
        obj = self._resolve_object(spec)
        self._apply_properties(obj, spec.get("properties", {}))
        objects = Ioc.resolve("Game.Objects", dict)
        objects[obj.id] = obj

    @staticmethod
    def _resolve_object(spec: dict) -> GameObjectBase:
        obj_type = spec["type"]
        try:
            obj = Ioc.resolve("Game.Init.Object." + obj_type, GameObjectBase, spec["id"])
        except Exception:
            raise GameInitError(f"Неизвестный тип объекта '{obj_type}'.") from None

        capabilities = spec.get("capabilities")
        if capabilities is not None:
            obj.capabilities.clear()
            obj.capabilities.update(cast(Iterable[str], capabilities))
        return obj

    @staticmethod
    def _apply_properties(obj: GameObjectBase, properties: dict):
        for prop_key, value in properties.items():
            interface_name, sep, prop_name = prop_key.partition(".")
            if not sep:
                raise GameInitError(f"Свойство '{prop_key}' должно иметь вид '<Интерфейс>.<свойство>'.")
            interface_type = _resolve_interface(interface_name)
            adapter = Ioc.resolve("Adapter", interface_type, interface_type, obj)
            setattr(adapter, prop_name, parse_value(value))


def _resolve_interface(interface_name: str) -> Type:
    interface_type = _INTERFACES.get(interface_name)
    if interface_type is not None:
        return interface_type
    try:
        return Ioc.resolve("Game.Init.Interface." + interface_name, Type)
    except Exception:
        raise GameInitError(f"Неизвестный интерфейс '{interface_name}'.") from None
