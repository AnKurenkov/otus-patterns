import logging
from queue import Queue

from src.space_battle.core.actions.base import ActionBase, ActionsLoopBase, ActionsQueueBase

logger = logging.getLogger(__name__)


class HardStopAction(ActionBase):
    """Команда для немедленной остановки ActionsLoop"""

    def __init__(self, actions_loop: ActionsLoopBase):
        self._actions_loop = actions_loop

    def execute(self):
        self._actions_loop.stop()


class SoftStopAction(ActionBase):
    """Команда для мягкой остановки ActionsLoop после обработки текущей очереди"""

    def __init__(self, actions_loop: ActionsLoopBase, queue: ActionsQueueBase | Queue):
        self._actions_loop = actions_loop
        self._queue = queue

    def execute(self):
        old_behaviour = self._actions_loop.behaviour

        def new_behaviour():
            if not self._queue.empty():
                old_behaviour()
            else:
                self._actions_loop.stop()

        self._actions_loop.behaviour = new_behaviour
