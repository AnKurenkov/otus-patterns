from abc import ABC, abstractmethod


class ActionBase(ABC):
    """Абстрактный базовый класс действия (команды) над игровым объектом"""

    @abstractmethod
    def execute(self):
        """Выполнить действие (команду) над игровым объектом"""


class ActionQueueBase(ABC):
    """Абстрактный базовый класс очереди действий (команд)"""

    @abstractmethod
    def put(self, action: ActionBase) -> bool:
        """Добавить действие (команду) в очередь"""

    @abstractmethod
    def get(self) -> ActionBase:
        """Получить действие (команду) из очереди"""


class ActionLoopBase(ABC):
    """Абстрактный базовый класс цикла обработки очереди действий (команд)"""

    _queue: ActionQueueBase

    @property
    @abstractmethod
    def queue(self) -> ActionQueueBase:
        """Получить очередь действий (команд)"""

    @queue.setter
    @abstractmethod
    def queue(self, queue: ActionQueueBase):
        """Задать очередь действий (команд)"""

    @abstractmethod
    def run(self):
        """Запуск цикла обработки действий (команд)"""

    @abstractmethod
    def stop(self):
        """Остановка цикла обработки действий (команд)"""
