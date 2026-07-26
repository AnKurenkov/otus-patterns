from abc import ABC, abstractmethod


class GameObjectBase(ABC):
    """Абстрактный базовый класс игрового объекта"""

    @property
    @abstractmethod
    def id(self):
        """Получить id игрового объекта"""
