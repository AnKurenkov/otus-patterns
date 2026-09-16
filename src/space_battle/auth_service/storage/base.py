from abc import ABC, abstractmethod


class GameRepository(ABC):
    """Контракт хранилища игр auth-сервиса."""

    @abstractmethod
    def create(self, game_id: str, participants: list[str]) -> None:
        """Сохраняет игру с заданными участниками."""

    @abstractmethod
    def exists(self, game_id: str) -> bool:
        """Возвращает True, если игра с таким id существует."""

    @abstractmethod
    def get_participants(self, game_id: str) -> list[str] | None:
        """Возвращает участников игры или None, если игры нет."""
