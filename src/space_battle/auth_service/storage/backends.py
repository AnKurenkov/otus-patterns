from typing import Callable

from src.space_battle.auth_service.storage.base import GameRepository
from src.space_battle.auth_service.storage.in_memory import InMemoryGameRepository
from src.space_battle.config import settings

_BACKENDS: dict[str, Callable[[], GameRepository]] = {}
_INSTANCES: dict[str, GameRepository] = {}


def register_backend(name: str, factory: Callable[[], GameRepository]) -> None:
    """Регистрирует фабрику бэкенда хранилища"""
    _BACKENDS[name] = factory


register_backend("in_memory", InMemoryGameRepository)


def create_game_repository() -> GameRepository:
    """Возвращает синглтон репозитория для активного бэкенда из настроек."""
    backend = settings.storage_backend
    if backend not in _BACKENDS:
        raise ValueError(
            f"Unknown storage backend '{backend}'. " f"Available backends: {', '.join(sorted(_BACKENDS))}."
        )
    if backend not in _INSTANCES:
        _INSTANCES[backend] = _BACKENDS[backend]()
    return _INSTANCES[backend]
