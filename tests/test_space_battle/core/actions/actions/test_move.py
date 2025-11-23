import math
from unittest.mock import PropertyMock, patch

import pytest

from src.space_battle.core.actions.actions import Move
from src.space_battle.core.base import Movable
from src.space_battle.core.exceptions import (
    GetLocationError,
    GetVelocityError,
    ObjectMoveError,
)
from src.space_battle.core.space import Point, PolarVelocity
from tests.test_space_battle.core import MovableStub


class TestMove:
    @staticmethod
    @pytest.mark.parametrize(
        "obj_",
        [MovableStub(Point(12, 5), PolarVelocity(7, 0)), MovableStub(Point(12, 5), PolarVelocity(7, 2 * math.pi))],
    )
    def test_move_polar_0(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == Point(19, 5)

    @staticmethod
    @pytest.mark.parametrize("obj_", [MovableStub(Point(12, 5), PolarVelocity(7, 0.5 * math.pi))])
    def test_move_polar_90(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == Point(12, 12)

    @staticmethod
    @pytest.mark.parametrize("obj_", [MovableStub(Point(12, 5), PolarVelocity(7, math.pi))])
    def test_move_polar_180(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == Point(5, 5)

    @staticmethod
    @pytest.mark.parametrize("obj_", [MovableStub(Point(12, 5), PolarVelocity(3, 1.5 * math.pi))])
    def test_move_polar_270(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == Point(12, 2)

    @staticmethod
    def test_get_location_error():
        obj_ = MovableStub(Point(-1, -1), PolarVelocity(7, 0))
        with pytest.raises(GetLocationError):
            with patch.object(MovableStub, "location", new_callable=PropertyMock) as mock_location:
                mock_location.side_effect = GetLocationError()
                Move(obj_).execute()

    @staticmethod
    def test_get_velocity_error():
        obj_ = MovableStub(Point(1, 1), PolarVelocity(0, 0))
        with pytest.raises(GetVelocityError):
            with patch.object(MovableStub, "velocity", new_callable=PropertyMock) as mock_velocity:
                mock_velocity.side_effect = GetVelocityError()
                Move(obj_).execute()

    @staticmethod
    def test_object_move_error():
        obj_ = MovableStub(Point(1, 1), PolarVelocity(7, math.pi))
        with pytest.raises(ObjectMoveError):
            with patch.object(Point, "move_to", new_callable=PropertyMock) as mock_move_to:
                mock_move_to.side_effect = ObjectMoveError()
                Move(obj_).execute()
