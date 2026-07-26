from src.space_battle.core.actions.game_actions import GameAction


class GameRouter:
    def __init__(self):
        self._games: dict[str, GameAction] = {}

    def register(self, game: GameAction) -> None:
        self._games[game.id] = game

    def get(self, game_id: str) -> GameAction:
        if game_id not in self._games:
            raise KeyError(f"Игра {game_id} не найдена")
        return self._games[game_id]


game_router = GameRouter()
