import logging
import uuid
from abc import ABC, abstractmethod
from queue import Queue
from time import perf_counter
from typing import Any

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.base import GameObjectBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import Scope

logging.basicConfig(level=logging.DEBUG)
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
        self._uuid = str(uuid.uuid4())  # TODO: определять в initial
        self._objects: dict[str, GameObjectBase] = {}  # TODO: определять в initial
        self._time = time_sec
        self._scheduler = scheduler
        self._queue = Queue()  # TODO: Ioc.resolve("Game.Queue.NonThreadSafe.Create", ActionsQueueBase)?
        self._scope: Scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game.Queue", lambda: self._queue).execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game.Objects", lambda: self._objects).execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game.IsOver", lambda: False).execute()
        # TODO: реализовать команды "Game.Init", "Game.Queue" (см. Урок 20, 1:10:00)
        #  что должно быть в макрокоманде "Game.Init": иниц. игрового поля - создать все игровые персонажи
        #  (корабли, топливо и др. свойства), расставить объекты, определить их поворот и т.п.,
        #  initial=None - информация для инициализации (словарик string: object)
        Ioc.resolve("IoC.Register", ActionBase, "Game.Init", lambda init: GameInitAction(init)).execute()
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

    @property
    def scope(self):
        return self._scope

    def register_object(self, obj: GameObjectBase):
        self._objects[obj.id] = obj

    def get_object(self, obj_id: str) -> GameObjectBase | None:
        return self._objects.get(obj_id, None)


class GameInitAction(ActionBase):
    def __init__(self, initial=None):
        self._initial = initial

    def execute(self):
        logger.debug("Выполнена команда GameInitAction.")
        # TODO: описать обработку initial


class GameStopAction(ActionBase):
    def execute(self):
        Ioc.resolve("IoC.Register", ActionBase, "Game.IsOver", lambda: True).execute()


class SchedulerAction(ActionBase, SchedulerBase):
    """Действие Планировщика"""

    # Цель Планировщика - выбрать очередную игру внутри потока, которую можем выполнить

    def __init__(self):
        self._queue = Queue()  # TODO: должна быть потокоНЕбезопасная очередь

    def add(self, game: GameAction):
        self._queue.put(game, block=False)
        # TODO: при добавлении в очередь извне ждать 100 мс новых команд, если их нет - планировать игру
        #  (см. Урок 20, 1:45:00)

    def has_work(self) -> bool:
        return not self._queue.empty()

    def execute(self):
        if not self._queue.empty():
            game = self._queue.get(block=False)
            game.execute()


# TODO: Добавить обработку SchedulerAction в ActionsLoop (ServerThread) (см. Урок 20, 1:34:00)
#  - добавил UseSchedulerAction в core.server.actions
