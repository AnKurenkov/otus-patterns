import math

import pytest

from src.space_battle.core.space import CartesianVector, Direction, Point, PolarVector, PolarVelocity


class TestVectorBase:
    def test_add_non_vector_raises(self):
        with pytest.raises(TypeError):
            CartesianVector(1, 1) + 5

    def test_eq_non_vector_raises(self):
        with pytest.raises(TypeError):
            CartesianVector(1, 1) == 5

    def test_repr(self):
        assert "CartesianVector" in repr(CartesianVector(1, 2))
        assert "Direction" in repr(Direction(3, 8))


class TestCartesianVector:
    def test_add_vectors(self):
        assert CartesianVector(1, 2) + CartesianVector(3, 4) == CartesianVector(4, 6)

    def test_magnitude(self):
        assert CartesianVector(3, 4).magnitude == pytest.approx(5.0)

    def test_magnitude_uses_raw_coordinates(self):
        assert CartesianVector(3.5, 4).magnitude == pytest.approx(math.hypot(3.5, 4))

    def test_angle(self):
        assert CartesianVector(1, 0).angle == pytest.approx(0.0)
        assert CartesianVector(0, 1).angle == pytest.approx(math.pi / 2)


class TestPolarVector:
    def test_negative_radius_raises(self):
        with pytest.raises(ValueError):
            PolarVector(-1, 0.0)

    def test_magnitude_equals_radius(self):
        assert PolarVector(5, 1.0).magnitude == 5

    def test_to_cartesian(self):
        assert PolarVector(1, 0.0).x == 1
        assert PolarVector(1, 0.0).y == 0


class TestPoint:
    def test_move_to(self):
        point = Point(1, 2)
        point.move_to(PolarVelocity(10, 0.0))
        assert point.x == 11
        assert point.y == 2


class TestDirection:
    def test_negative_direction_normalized(self):
        direction = Direction(-1, 8)
        assert direction.d >= 0
        assert direction.n == 8

    def test_rotate_by(self):
        direction = Direction(0, 8)
        direction.rotate_by(3)
        assert direction.d == 3

    def test_rotate_by_negative(self):
        direction = Direction(0, 8)
        direction.rotate_by(-2)
        assert direction.d == 6

    def test_negative_modulus_keeps_negative_direction(self):
        direction = Direction(1, -8)
        assert direction.d < 0
        direction.rotate_by(1)
        assert direction.d < 0

    def test_eq_non_direction_raises(self):
        with pytest.raises(TypeError):
            Direction(3, 8) == 42

    def test_eq_ignores_graduations(self):
        assert Direction(3, 8) == Direction(3, 16)
