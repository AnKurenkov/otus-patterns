from abc import ABC, abstractmethod

from src.space_battle.core.space import Direction, Point, VectorBase

# TODO: перенести в core.objects??


class Movable(ABC):
    """Абстрактный базовый класс для движущихся прямолинейно объектов"""

    @property
    @abstractmethod
    def location(self) -> Point:
        """Получить координаты объекта"""

    @location.setter
    @abstractmethod
    def location(self, location: Point):
        """Задать координаты объекта"""

    @property
    @abstractmethod
    def velocity(self) -> VectorBase:
        """Получить вектор скорости объекта"""

    @velocity.setter
    @abstractmethod
    def velocity(self, velocity: VectorBase):
        """Задать вектор скорости объекта"""


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
