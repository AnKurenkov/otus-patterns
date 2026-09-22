from abc import ABC, abstractmethod

from src.space_battle.core.space import Point, PolarVelocity


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
    def velocity(self) -> PolarVelocity:
        """Получить вектор скорости объекта"""

    @velocity.setter
    @abstractmethod
    def velocity(self, velocity: PolarVelocity):
        """Задать вектор скорости объекта"""
