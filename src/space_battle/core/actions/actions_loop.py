import threading

from src.space_battle.core.ioc import Ioc

from .base import ActionBase, ActionsLoopBase, ActionsQueueBase


class ActionsLoop(ActionsLoopBase):
    """Цикл обработки действий (команд)"""

    def __init__(self, queue: ActionsQueueBase):
        self._running = False
        self._queue = queue
        self._behaviour = self._default_behaviour
        self._thread = threading.Thread(target=self._loop)

    def _loop(self):
        # self._before()
        while self._running:
            self._behaviour()
        # self._after()

    def _default_behaviour(self):
        action = self._queue.get()
        try:
            action.execute()
        except Exception as e:
            Ioc.resolve("HandleException", ActionBase, action, e).execute()

    @property
    def behaviour(self):
        return self._behaviour

    @behaviour.setter
    def behaviour(self, behaviour):
        self._behaviour = behaviour

    def run(self):
        """Запуск цикла обработки действий (команд)"""
        self._thread.start()

    def stop(self):
        """Остановка цикла обработки действий (команд)"""
        self._running = False
