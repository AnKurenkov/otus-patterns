import math
from abc import ABC, abstractmethod


class VectorBase(ABC):
    """Абстрактный базовый класс для векторов."""

    @property
    @abstractmethod
    def x(self):
        """Возвращает x-компоненту вектора."""

    @property
    @abstractmethod
    def y(self):
        """Возвращает y-компоненту вектора."""

    @abstractmethod
    def magnitude(self):
        """Возвращает длину (модуль) вектора."""

    @abstractmethod
    def angle(self):
        """Возвращает угол в радианах от оси X."""

    def __add__(self, other):
        """Складывает текущий вектор с другим и возвращает новый вектор в декартовых координатах."""
        if not isinstance(other, VectorBase):
            raise TypeError("Можно складывать только с другим вектором с типом VectorBase")
        return CartesianVector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        """Сравнивает текущий вектор с другим."""
        if not isinstance(other, VectorBase):
            raise TypeError("Можно сравнивать только с другим вектором с типом VectorBase")
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x:.3f}, {self.y:.3f})"


class CartesianVector(VectorBase):
    """Вектор в декартовых координатах. Координаты округляются до целых значений."""

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return round(self._x)

    @property
    def y(self) -> int:
        return round(self._y)

    @property
    def magnitude(self) -> int:
        return round(math.hypot(self._x, self._y))

    @property
    def angle(self) -> int:
        return round(math.atan2(self._y, self._x))


class PolarVector(VectorBase):
    """Вектор в полярных координатах (r, theta). Координаты округляются до целых значений."""

    def __init__(self, r: float, theta: float):
        if r < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self._r = r
        self._theta = theta  # угол в радианах

    @property
    def x(self) -> int:
        return round(self._r * math.cos(self._theta))

    @property
    def y(self) -> int:
        return round(self._r * math.sin(self._theta))

    @property
    def magnitude(self) -> int:
        return round(self._r)

    @property
    def angle(self) -> int:
        return round(self._theta)


class Point(CartesianVector):
    def move_to(self, velocity: VectorBase):
        self._x += velocity.x
        self._y += velocity.y
        return self
