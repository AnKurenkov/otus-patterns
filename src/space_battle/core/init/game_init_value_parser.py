from typing import Any, Callable

from src.space_battle.core.init.game_init_exception import GameInitError
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.space import Direction, Point, PolarVelocity

_VALUE_PARSERS: dict[str, Callable[[Any], Any]] = {
    "Point": lambda raw: Point(raw["x"], raw["y"]),
    "PolarVelocity": lambda raw: PolarVelocity(raw["r"], raw["theta"]),
    "Direction": lambda raw: Direction(raw["d"], raw["n"]),
}


def parse_value(value: Any) -> Any:
    """Преобразовать значение свойства из `initial` в типизированный объект.

    Скаляры (int/float/str/bool) возвращаются как есть. Словари распознаются
    по схеме: x/y -> Point, r/theta -> PolarVelocity, d/n -> Direction.
    Явная форма {"type": ..., "value": ...} поддерживает расширение через
    реестр "Game.Init.Value.<type>".
    """
    if not isinstance(value, dict):
        return value

    keys = set(value.keys())
    if {"x", "y"} <= keys:
        return Point(value["x"], value["y"])
    if {"r", "theta"} <= keys:
        return PolarVelocity(value["r"], value["theta"])
    if {"d", "n"} <= keys:
        return Direction(value["d"], value["n"])
    if "type" in value and "value" in value:
        return _parse_typed_value(value["type"], value["value"])
    raise GameInitError(f"Неизвестная схема значения свойства: {value!r}")


def _parse_typed_value(value_type: str, raw: Any) -> Any:
    parser = _VALUE_PARSERS.get(value_type)
    if parser is None:
        try:
            parser = Ioc.resolve("Game.Init.Value." + value_type, Callable)
        except Exception:
            parser = None
    if parser is None:
        raise GameInitError(f"Неизвестный тип значения '{value_type}'.")
    return parser(raw)
