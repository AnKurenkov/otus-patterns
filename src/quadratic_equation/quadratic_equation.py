import math


class QuadraticEquation:
    tolerance = 1e-10

    def __init__(self, a: float, b: float, c: float, tolerance=1e-10):
        self.a = a
        self.b = b
        self.c = c
        self.tolerance = tolerance

    def _check_coef_for_nan_inf(self, coefficient):
        if not math.isfinite(coefficient):
            raise ValueError(f"Коэффициент не может быть равен NaN или inf. "
                             f"Коэффициенты: a={self.a}, b={self.b}, c={self.c}.")

    def _is_close(self, val1: float, val2: float):
        return math.isclose(val1, val2, abs_tol=self.tolerance)

    def solve(self) -> list[float]:
        self._check_coef_for_nan_inf(self.a)
        self._check_coef_for_nan_inf(self.b)
        self._check_coef_for_nan_inf(self.c)

        if self._is_close(self.a, 0.0):
            raise ValueError("Коэффициент a не может быть равен 0 в квадратном уравнении.")
        d = self.b*self.b - 4*self.a*self.c
        if self._is_close(d, 0.0):
            return [-self.b/(2*self.a), -self.b/(2*self.a)]
        elif d > 0:
            return [-self.b+(d**0.5)/(2*self.a), -self.b-(d**0.5)/(2*self.a)]
        else:
            return []
