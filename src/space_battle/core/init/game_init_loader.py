import json
from pathlib import Path
from typing import Dict, Union

from src.space_battle.core.init.game_init_exception import GameInitError


def load_initial_from_json(source: Union[str, Path]) -> Dict:
    """Загрузить initial-данные из JSON-файла или JSON-строки.

    Если `source` указывает на существующий файл — читается файл,
    иначе `source` интерпретируется как JSON-строка.
    """
    text = _read_source(source)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GameInitError(f"Некорректный JSON в initial: {exc}") from exc
    if not isinstance(data, dict):
        raise GameInitError(f"Корневой элемент initial должен быть объектом (dict), получено: {type(data)!r}")
    return data


def _read_source(source: Union[str, Path]) -> str:
    path = Path(source)
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GameInitError(f"Не удалось прочитать файл конфигурации '{source}': {exc}") from exc
    return str(source)
