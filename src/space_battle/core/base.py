from abc import ABC, abstractmethod

from src.space_battle.models.vector import Point, VectorBase


class Movable(ABC):
    """Абстрактный базовый класс для движущихся объектов"""

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
