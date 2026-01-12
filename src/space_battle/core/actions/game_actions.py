import logging
import uuid
from abc import ABC, abstractmethod
from queue import Queue
from time import perf_counter
from typing import Any

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import Scope

logger = logging.getLogger(__name__)


class SchedulerBase(ABC):
    @abstractmethod
    def add(self, action: ActionBase):
        """Добавить Действие в очередь Планировщика"""

    @abstractmethod
    def has_work(self) -> bool:
        """Проверка наличия Действий в очереди Планировщика"""


class GameAction(ActionBase):
    """Действие Игры"""

    def __init__(self, time_sec: float, scheduler: SchedulerBase):
        self._uuid = uuid.uuid4()
        self._time = time_sec
        self._scheduler = scheduler
        self._queue = Queue()  # TODO: Ioc.resolve("Game.Queue.NonThreadSafe.Create", ActionsQueueBase)?
        self._scope: Scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()
        # TODO: реализовать команды "Game.Init", "Game.queue" (см. Урок 20, 1:10:00)
        # Ioc.resolve("IoC.Register", ActionBase, "Game.Queue", self._queue)
        # self._queue.put(Ioc.resolve("Game.Init", ActionBase, initial))

    def execute(self):
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()

        stop = False
        # stop = Ioc.resolve("Game.IsOver", bool)  # TODO: Иниц. флаг "Game.IsOver" в команде "Game.Init"

        current_time = perf_counter()
        while not stop and (current_time + self._time > perf_counter()):
            if not self._queue.empty():
                action = self._queue.get(block=False)
                action.execute()

        if not stop:
            self._scheduler.add(self)

    @property
    def id(self):
        return self._uuid

    @property
    def queue(self):
        return self._queue


class SchedulerAction(ActionBase, SchedulerBase):
    """Действие Планировщика"""

    def __init__(self):
        self._queue = Queue()

    def add(self, action: ActionBase):
        self._queue.put(action, block=False)

    def has_work(self) -> bool:
        return self._queue.empty()

    def execute(self):
        if not self._queue.empty():
            action = self._queue.get(block=False)
            action.execute()


# TODO: Добавить обработку SchedulerAction в ActionsLoop (ServerThread) (см. Урок 20, 1:40:00)
