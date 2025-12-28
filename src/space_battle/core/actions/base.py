from abc import ABC, abstractmethod


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

    _queue: ActionsQueueBase

    @abstractmethod
    def run(self):
        """Запуск цикла обработки действий (команд)"""

    @abstractmethod
    def stop(self):
        """Остановка цикла обработки действий (команд)"""
