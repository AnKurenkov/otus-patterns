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

    def __init__(self, time_sec: float, scheduler: SchedulerBase, initial=None):
        self._uuid = uuid.uuid4()
        self._time = time_sec
        self._scheduler = scheduler
        self._queue = Queue()  # TODO: Ioc.resolve("Game.Queue.NonThreadSafe.Create", ActionsQueueBase)?
        self._scope: Scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()
        # TODO: реализовать команды "Game.Init", "Game.queue" (см. Урок 20, 1:10:00)
        Ioc.resolve("IoC.Register", ActionBase, "Game.Queue", lambda: self._queue).execute()
        # self._queue.put(Ioc.resolve("Game.Init", ActionBase, initial))
        Ioc.resolve("Game.Init", ActionBase, initial).execute()

    def execute(self):
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()

        current_time = perf_counter()
        while not Ioc.resolve("Game.IsOver", bool) and (current_time + self._time > perf_counter()):
            if not self._queue.empty():
                action = self._queue.get(block=False)
                action.execute()

        if not Ioc.resolve("Game.IsOver", bool):
            self._scheduler.add(self)

    @property
    def id(self):
        return self._uuid

    @property
    def queue(self):
        return self._queue


class GameInitAction(ActionBase):
    def __init__(self, initial=None):
        self._initial = initial

    def execute(self):
        Ioc.resolve("IoC.Register", ActionBase, "Game.IsOver", lambda: False).execute()


class GameStopAction(ActionBase):
    def execute(self):
        Ioc.resolve("IoC.Register", ActionBase, "Game.IsOver", lambda: True).execute()


class SchedulerAction(ActionBase, SchedulerBase):
    """Действие Планировщика"""

    def __init__(self):
        self._queue = Queue()

    def add(self, action: ActionBase):
        self._queue.put(action, block=False)

    def has_work(self) -> bool:
        return not self._queue.empty()

    def execute(self):
        if not self._queue.empty():
            action = self._queue.get(block=False)
            action.execute()


# TODO: Добавить обработку SchedulerAction в ActionsLoop (ServerThread) (см. Урок 20, 1:40:00)
#  - добавил UseSchedulerAction в core.server.actions
