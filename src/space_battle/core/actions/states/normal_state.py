from queue import Empty
from typing import TYPE_CHECKING, Optional

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

from .base import ActionsLoopStateBase
from .commands import HardStopCommand, MoveToCommand

if TYPE_CHECKING:
    from src.space_battle.core.actions.base import ActionsLoopBase


class NormalState(ActionsLoopStateBase):
    """
    "Обычное" состояние: очередная команда извлекается из очереди и выполняется.

    - HardStopCommand -> None (остановка потока).
    - MoveToCommand -> переход в состояние MoveTo.
    - любая другая команда -> выполняется, состояние не меняется.
    """

    def handle(self, actions_loop: "ActionsLoopBase") -> Optional[ActionsLoopStateBase]:
        action = self._get_next_action(actions_loop)
        if action is None:
            return self

        if isinstance(action, HardStopCommand):
            return None

        if isinstance(action, MoveToCommand):
            return Ioc.resolve("ActionsLoop.State.MoveTo", ActionsLoopStateBase, action.target_queue)

        try:
            action.execute()
        except Exception as e:
            Ioc.resolve("HandleException", ActionBase, action, e).execute()

        return self

    @staticmethod
    def _get_next_action(actions_loop: "ActionsLoopBase") -> Optional[ActionBase]:
        try:
            return actions_loop.queue.get(timeout=0.1)
        except Empty:
            return None
