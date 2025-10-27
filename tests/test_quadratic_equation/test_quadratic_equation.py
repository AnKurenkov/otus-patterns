import math

import pytest

from quadratic_equation import QuadraticEquation


class TestSolveQuadraticEquation:
    @staticmethod
    def test_no_roots():
        assert len(QuadraticEquation(a=1.0, b=0.0, c=1.0).solve()) == 0

    @staticmethod
    def test_two_roots():
        tolerance = QuadraticEquation.tolerance
        qe = QuadraticEquation(a=1.0, b=0.0, c=-1.0)
        roots = qe.solve()
        assert len(roots) > 0
        assert not math.isclose(roots[0], roots[1], abs_tol=tolerance)
        assert math.isclose(abs(roots[0]), 1.0, abs_tol=tolerance)
        assert math.isclose(abs(roots[1]), 1.0, abs_tol=tolerance)

    @staticmethod
    def test_one_root():
        tolerance = QuadraticEquation.tolerance
        qe = QuadraticEquation(a=1.0, b=2.0, c=1.0)
        roots = qe.solve()
        assert len(roots) > 0
        assert math.isclose(roots[0], roots[1], abs_tol=tolerance)
        assert math.isclose(roots[0], -1.0, abs_tol=tolerance)

    @staticmethod
    def test_a_is_close_zero():
        tolerance = QuadraticEquation.tolerance
        qe = QuadraticEquation(a=tolerance / 10, b=2.0, c=1.0)
        with pytest.raises(ValueError, match=r"Коэффициент a не может быть равен 0 в квадратном уравнении."):
            qe.solve()

    @staticmethod
    def test_d_is_close_zero():
        tolerance = QuadraticEquation.tolerance
        b = 2.0 + tolerance / 10
        qe = QuadraticEquation(a=1.0, b=b, c=1.0)
        roots = qe.solve()
        assert len(roots) > 0
        assert math.isclose(roots[0], roots[1], abs_tol=tolerance)
        assert math.isclose(roots[0], -1.0, abs_tol=tolerance)

    @staticmethod
    def test_a_is_nan():
        qe = QuadraticEquation(a=math.nan, b=2.0, c=1.0)
        with pytest.raises(ValueError, match=r"Коэффициент не может быть равен NaN или inf."):
            qe.solve()

    @staticmethod
    def test_b_is_inf():
        qe = QuadraticEquation(a=1.0, b=math.inf, c=1.0)
        with pytest.raises(ValueError, match=r"Коэффициент не может быть равен NaN или inf."):
            qe.solve()

    @staticmethod
    def test_c_is_neg_inf():
        qe = QuadraticEquation(a=1.0, b=2.0, c=-math.inf)
        with pytest.raises(ValueError, match=r"Коэффициент не может быть равен NaN или inf."):
            qe.solve()
