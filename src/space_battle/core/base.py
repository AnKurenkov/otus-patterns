from abc import ABC, abstractmethod

from src.space_battle.core.space import Direction, Point, PolarVelocity


class GameObjectBase(ABC):
    """Абстрактный базовый класс для игрового объекта"""  # TODO: перенести отсюда

    @property
    @abstractmethod
    def id(self):
        """Получить id объекта"""


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


class Fuelable(ABC):
    """Абстрактный базовый класс для заправляемых топливом объектов"""

    @property
    @abstractmethod
    def fuel(self) -> int:
        """Получить объем топлива объекта"""

    @fuel.setter
    @abstractmethod
    def fuel(self, fuel: int):
        """Задать объем топлива объекта"""

    @property
    @abstractmethod
    def fuel_consumption(self) -> int:
        """Получить мгновенный расход топлива объекта"""
