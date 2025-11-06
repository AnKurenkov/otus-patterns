from ..exceptions.base import SpaceBattleError
from ..exceptions.exception_handler import ExceptionHandler
from .base import ActionLoopBase, ActionQueueBase


class ActionLoop(ActionLoopBase):
    """Цикл обработки действий (команд)"""

    def __init__(self):
        self._is_running = False

    @property
    def queue(self) -> ActionQueueBase:
        """Получить очередь действий (команд)"""
        return self._queue

    @queue.setter
    def queue(self, queue: ActionQueueBase):
        """Задать очередь действий (команд)"""
        self._queue = queue

    def run(self):
        """Запуск цикла обработки действий (команд)"""
        while self._is_running:
            action = self._queue.get()
            try:
                action.execute()
            except SpaceBattleError as e:
                ExceptionHandler.handle(action, e)

    def stop(self):
        """Остановка цикла обработки действий (команд)"""
        self._is_running = False
