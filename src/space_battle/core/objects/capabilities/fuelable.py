from abc import ABC, abstractmethod


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

    @fuel_consumption.setter
    @abstractmethod
    def fuel_consumption(self, fuel_consumption: int):
        """Задать мгновенный расход топлива объекта"""
