import logging

from src.space_battle.core.actions.base import ActionBase, ActionsLoopBase

logger = logging.getLogger(__name__)


class HardStopAction(ActionBase):
    """Команда для немедленной остановки ActionsLoop"""

    def __init__(self, actions_loop: ActionsLoopBase):
        self._actions_loop = actions_loop

    def execute(self):
        if self._actions_loop.is_in_thread:
            self._actions_loop.stop()
        else:
            raise Exception("Попытка остановить очередь из другого потока.")


class SoftStopAction(ActionBase):
    """Команда для мягкой остановки ActionsLoop после обработки текущей очереди"""

    def __init__(self, actions_loop: ActionsLoopBase):
        self._actions_loop = actions_loop

    def execute(self):
        old_behaviour = self._actions_loop.behaviour

        def new_behaviour():
            if not self._actions_loop.queue.empty():
                old_behaviour()
            else:
                if self._actions_loop.is_in_thread:
                    self._actions_loop.stop()
                else:
                    raise Exception("Попытка остановить очередь из другого потока.")

        self._actions_loop.behaviour = new_behaviour
