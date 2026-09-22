import logging
from queue import Queue
from typing import Any, Optional

from src.space_battle.config import settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, SchedulerAction
from src.space_battle.core.init.register_game_dependencies import RegisterGameDependenciesAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.actions import UseSchedulerAction
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.server_thread import ServerThread

logger = logging.getLogger(__name__)


class GameRuntime:
    """Рантайм игрового сервера: планировщик игр и поток обработки команд."""

    def __init__(self):
        RegisterGameDependenciesAction().execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game", lambda *args: GameAction(*args)).execute()
        self._scheduler = SchedulerAction()
        self._thread = ServerThread(Queue(), daemon=True)
        self._thread.queue.put(UseSchedulerAction(self._thread, self._scheduler))
        self._thread.run()

    def create_game(self, initial: dict[str, Any]) -> GameAction:
        game: GameAction = Ioc.resolve("Game", GameAction, settings.game_tick_seconds, self._scheduler, initial)
        game_router.register(game)
        self._scheduler.add(game)
        return game

    def stop(self):
        self._thread.stop()


_game_runtime: Optional[GameRuntime] = None


def get_game_runtime() -> GameRuntime:
    global _game_runtime
    if _game_runtime is None:
        _game_runtime = GameRuntime()
    return _game_runtime
