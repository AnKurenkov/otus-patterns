from abc import ABC, abstractmethod

from src.space_battle.core.space import Direction


class Rotatable(ABC):
    """Абстрактный базовый класс для вращающихся объектов"""

    @property
    @abstractmethod
    def direction(self) -> Direction:
        """Получить направление объекта"""

    @direction.setter
    @abstractmethod
    def direction(self, direction: Direction):
        """Задать направление объекта"""

    @property
    @abstractmethod
    def angular_velocity(self) -> int:
        """Получить мгновенную угловую скорость объекта"""

    @angular_velocity.setter
    @abstractmethod
    def angular_velocity(self, angular_velocity: int):
        """Задать мгновенную угловую скорость объекта"""
