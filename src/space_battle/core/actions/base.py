from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
from typing import Callable


class ActionBase(ABC):
    """Абстрактный базовый класс действия (команды) над игровым объектом"""

    @abstractmethod
    def execute(self):
        """Выполнить действие (команду) над игровым объектом"""


class ActionsQueueBase(ABC):
    """Абстрактный базовый класс очереди действий (команд)"""

    @abstractmethod
    def put(self, action: ActionBase, *args, **kwargs):
        """Добавить действие (команду) в очередь"""

    @abstractmethod
    def get(self, *args, **kwargs) -> ActionBase:
        """Получить действие (команду) из очереди"""


class ActionsLoopBase(ABC):
    """Абстрактный базовый класс цикла обработки очереди действий (команд)"""

    _queue: ActionsQueueBase | Queue
    _thread: Thread

    @property
    @abstractmethod
    def queue(self) -> ActionsQueueBase | Queue:
        """Получить очередь действий (команд)"""

    @property
    @abstractmethod
    def is_in_thread(self) -> bool:
        """Проверить нахождение в текущем потоке"""

    @property
    @abstractmethod
    def behaviour(self) -> Callable[[], None]:
        """Получить поведение цикла обработки действий (команд)"""

    @behaviour.setter
    @abstractmethod
    def behaviour(self, behaviour: Callable[[], None]):
        """Задать поведение цикла обработки действий (команд)"""

    @property
    @abstractmethod
    def before(self) -> Callable[[], None]:
        """Получить поведение перед циклом обработки действий (команд)"""

    @before.setter
    @abstractmethod
    def before(self, before: Callable[[], None]):
        """Задать поведение перед циклом обработки действий (команд)"""

    @property
    @abstractmethod
    def after(self) -> Callable[[], None]:
        """Получить поведение после цикла обработки действий (команд)"""

    @after.setter
    @abstractmethod
    def after(self, after: Callable[[], None]):
        """Задать поведение после цикла обработки действий (команд)"""

    @abstractmethod
    def run(self):
        """Запуск цикла обработки действий (команд)"""

    @abstractmethod
    def stop(self):
        """Остановка цикла обработки действий (команд)"""
