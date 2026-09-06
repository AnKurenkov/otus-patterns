import math

from src.space_battle.core.actions.actions import ChangeVelocity
from src.space_battle.core.space import Direction, Point, PolarVelocity
from tests.test_space_battle.core import MovableStub, RotatableStub, SpaceshipStub


class TestChangeVelocity:
    @staticmethod
    def test_change_velocity():
        d = 64
        n = 255
        obj_ = SpaceshipStub(
            location=Point(12, 5), velocity=PolarVelocity(7, 0 * math.pi), direction=Direction(d, n), angular_velocity=1
        )
        ChangeVelocity(obj_).execute()
        assert obj_.velocity.angle == d / (n + 1) * 2 * math.pi

    @staticmethod
    def test_no_change_velocity_error_for_rotatable():
        obj_ = RotatableStub(Direction(2, 255), 0)
        ChangeVelocity(obj_).execute()

    @staticmethod
    def test_no_change_velocity_for_movable():
        obj_ = MovableStub(Point(12, 5), PolarVelocity(7, 0 * math.pi))
        ChangeVelocity(obj_).execute()
        assert obj_.velocity.angle == 0
