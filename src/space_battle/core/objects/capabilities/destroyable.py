from abc import ABC, abstractmethod


class Destroyable(ABC):
    """Абстрактный базовый класс для разрушаемых объектов"""

    @property
    @abstractmethod
    def health(self) -> int:
        """Получить здоровье объекта"""

    @health.setter
    @abstractmethod
    def health(self, health: int):
        """Задать здоровье объекта"""
