from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.game_router import game_router
from src.space_battle.game_server.models import AgentMessageModel


class InterpretAction(ActionBase):
    """
    Команда-интерпретатор.
    1. Находит игру по game_id.
    2. Находит игровой объект по object_id.
    3. Через IoC резолвит конкретную команду по action_id, передавая ей объект и args.
    4. Полученную команду кладёт в очередь той же игры.
    """

    def __init__(self, message: AgentMessageModel):
        self._msg: AgentMessageModel = message

    def execute(self) -> None:
        game: GameAction = game_router.get(self._msg.game_id)
        obj = game.get_object(self._msg.object_id)
        action = Ioc.resolve(self._msg.action_id, ActionBase, obj, self._msg.data)
        game.queue.put(action)
