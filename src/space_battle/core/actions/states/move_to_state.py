from queue import Empty, Queue
from typing import TYPE_CHECKING, Optional

from src.space_battle.core.actions.base import ActionBase, ActionsQueueBase
from src.space_battle.core.ioc import Ioc

from .base import ActionsLoopStateBase
from .commands import HardStopCommand, RunCommand

if TYPE_CHECKING:
    from src.space_battle.core.actions.base import ActionsLoopBase


class MoveToState(ActionsLoopStateBase):
    """
    Состояние MoveTo: очередная команда извлекается из очереди и перенаправляется
    (без выполнения) в другую очередь `target_queue`.

    - HardStopCommand -> None (остановка потока).
    - RunCommand -> переход в "обычное" состояние.
    - любая другая команда -> перенаправляется в target_queue, состояние не меняется.
    """

    def __init__(self, target_queue: ActionsQueueBase | Queue):
        self._target_queue = target_queue

    def handle(self, actions_loop: "ActionsLoopBase") -> Optional[ActionsLoopStateBase]:
        action = self._get_next_action(actions_loop)
        if action is None:
            return self

        if isinstance(action, HardStopCommand):
            return None

        if isinstance(action, RunCommand):
            return Ioc.resolve("ActionsLoop.State.Normal", ActionsLoopStateBase)

        self._target_queue.put(action)
        return self

    @staticmethod
    def _get_next_action(actions_loop: "ActionsLoopBase") -> Optional[ActionBase]:
        try:
            return actions_loop.queue.get(timeout=0.1)
        except Empty:
            return None
