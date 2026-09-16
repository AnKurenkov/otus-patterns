from src.space_battle.auth_service.storage.base import GameRepository


class InMemoryGameRepository(GameRepository):
    """Адаптер хранилища поверх in-memory словаря.

    Формат данных: {game_id: [user_id_1, user_id_2, ...]}.
    """

    def __init__(self) -> None:
        self._games: dict[str, list[str]] = {}

    def create(self, game_id: str, participants: list[str]) -> None:
        self._games[game_id] = participants

    def exists(self, game_id: str) -> bool:
        return game_id in self._games

    def get_participants(self, game_id: str) -> list[str] | None:
        return self._games.get(game_id)

    def clear(self) -> None:
        """Очищает хранилище (используется в тестах)."""
        self._games.clear()
