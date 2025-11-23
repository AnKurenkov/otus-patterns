import math

from src.space_battle.core.actions.actions import ChangeVelocity, Rotate
from src.space_battle.core.actions.macro_actions import RotateWithChangeVelocity
from src.space_battle.core.objects.spaceship import Spaceship
from src.space_battle.core.space import Direction, Point, PolarVelocity


class TestRotateWithChangeVelocity:
    @staticmethod
    def test_rotate_with_change_velocity():
        d = 64
        n = 255
        obj_ = Spaceship(
            location=Point(12, 5), velocity=PolarVelocity(7, 0 * math.pi), direction=Direction(d, n), angular_velocity=1
        )
        ChangeVelocity(obj_).execute()
        RotateWithChangeVelocity((Rotate(obj_), ChangeVelocity(obj_)))
        assert obj_.velocity.angle == d / (n + 1) * 2 * math.pi
