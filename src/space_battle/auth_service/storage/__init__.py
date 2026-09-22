from src.space_battle.auth_service.storage.backends import create_game_repository, register_backend
from src.space_battle.auth_service.storage.base import GameRepository
from src.space_battle.auth_service.storage.in_memory import InMemoryGameRepository

__all__ = [
    "GameRepository",
    "InMemoryGameRepository",
    "create_game_repository",
    "register_backend",
]
