import threading
from queue import Empty, Queue
from typing import Callable

from src.space_battle.core.ioc import Ioc

from .base import ActionBase, ActionsLoopBase, ActionsQueueBase


class ActionsLoop(ActionsLoopBase):
    """Цикл обработки действий (команд)"""

    def __init__(self, queue: ActionsQueueBase | Queue):
        self._running = False
        self._queue = queue
        self._behaviour = self._default_behaviour
        self._before = self._default_before
        self._after = self._default_after
        self._thread = threading.Thread(target=self._loop)

    def _loop(self):
        self._before()
        while self._running:
            self._behaviour()
        self._after()

    def _default_behaviour(self):
        action = None
        try:
            action = self._queue.get(timeout=0.5)
        except Empty:
            pass
        if action:
            try:
                action.execute()
            except Exception as e:
                Ioc.resolve("HandleException", ActionBase, action, e).execute()

    def _default_before(self):
        pass

    def _default_after(self):
        pass

    @property
    def behaviour(self) -> Callable[[], None]:
        return self._behaviour

    @behaviour.setter
    def behaviour(self, behaviour: Callable[[], None]):
        self._behaviour = behaviour

    @property
    def before(self) -> Callable[[], None]:
        return self._before

    @before.setter
    def before(self, before: Callable[[], None]):
        self._before = before

    @property
    def after(self) -> Callable[[], None]:
        return self._after

    @after.setter
    def after(self, after: Callable[[], None]):
        self._after = after

    def run(self):
        """Запуск цикла обработки действий (команд)"""
        self._running = True
        self._thread.start()

    def stop(self):
        """Остановка цикла обработки действий (команд)"""
        self._running = False
        # self._thread.join(timeout=1)  # TODO: подумать над использованием
