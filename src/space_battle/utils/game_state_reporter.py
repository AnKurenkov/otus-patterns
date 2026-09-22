import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO, Union

from src.space_battle.core.actions.game_actions import GameAction
from src.space_battle.core.exceptions.exceptions import ObjectCapabilityError
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Fuelable, Movable, Rotatable
from src.space_battle.core.objects.game_object_base import GameObjectBase

logger = logging.getLogger(__name__)


def _read_properties(obj: GameObjectBase) -> dict:
    """Прочитать доступные для отладки свойства объекта через адаптеры способностей."""
    props = {"id": obj.id, "type": obj.type}

    try:
        movable = Ioc.resolve("Adapter", Movable, Movable, obj)
        try:
            props["location"] = {"x": movable.location.x, "y": movable.location.y}
        except KeyError:
            pass
        try:
            props["velocity"] = {"r": movable.velocity.magnitude, "theta": round(movable.velocity.angle, 4)}
        except KeyError:
            pass
    except ObjectCapabilityError:
        pass

    try:
        rotatable = Ioc.resolve("Adapter", Rotatable, Rotatable, obj)
        try:
            props["direction"] = {"d": rotatable.direction.d, "n": rotatable.direction.n}
        except KeyError:
            pass
        try:
            props["angular_velocity"] = rotatable.angular_velocity
        except KeyError:
            pass
    except ObjectCapabilityError:
        pass

    try:
        fuelable = Ioc.resolve("Adapter", Fuelable, Fuelable, obj)
        try:
            props["fuel"] = fuelable.fuel
        except KeyError:
            pass
        try:
            props["fuel_consumption"] = fuelable.fuel_consumption
        except KeyError:
            pass
    except ObjectCapabilityError:
        pass

    try:
        props["owner"] = obj.get_property("owner")
    except KeyError:
        pass

    return props


def format_game_state(game: GameAction) -> str:
    """Сформировать строку с отладочным описанием текущего состояния игры."""
    lines = [f"[Game] id={game.id} field={game.field} objects={len(game.objects)}"]
    for obj in game.objects.values():
        lines.append(f"  [Object] {_read_properties(obj)}")
    return "\n".join(lines)


def game_state_dict(game: GameAction) -> dict:
    """Сформировать словарь с текущим состоянием игры для отладочного endpoint."""
    return {
        "id": game.id,
        "field": game.field,
        "objects": [_read_properties(obj) for obj in game.objects.values()],
    }


def report_game_state(game: GameAction, out: Optional[Union[str, Path, TextIO]] = None) -> str:
    """Вывести состояние игры в консоль и, при необходимости, дописать в файл."""
    text = format_game_state(game)
    timestamp = datetime.now().isoformat(timespec="seconds")
    log_line = f"[{timestamp}]\n{text}"
    logger.debug(log_line)
    if out is not None:
        if isinstance(out, (str, Path)):
            path = Path(out)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as file:
                file.write(log_line + "\n")
        else:
            out.write(log_line + "\n")
            out.flush()
    return text
