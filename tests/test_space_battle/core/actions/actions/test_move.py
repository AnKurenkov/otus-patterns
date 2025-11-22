from unittest.mock import PropertyMock, patch

import pytest

from space_battle.core.actions.actions import Move
from src.space_battle.core.base import Movable
from src.space_battle.core.exceptions import (
    GetLocationError,
    GetVelocityError,
    ObjectMoveError,
)
from src.space_battle.core.space import CartesianVelocity, Point, VectorBase


class MovableStub(Movable):
    def __init__(self, location: Point, velocity: VectorBase):
        self._location = location
        self._velocity = velocity

    @property
    def location(self) -> Point:
        return self._location

    @location.setter
    def location(self, location: Point):
        self._location = location

    @property
    def velocity(self) -> VectorBase:
        return self._velocity


class TestMove:
    @staticmethod
    @pytest.mark.parametrize("obj_", [MovableStub(Point(12, 5), CartesianVelocity(-7, 3))])
    def test_move(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == CartesianVelocity(5, 8)

    @staticmethod
    def test_get_location_error():
        obj_ = MovableStub(Point(-1, -1), CartesianVelocity(1, 1))
        with pytest.raises(GetLocationError):
            with patch.object(MovableStub, "location", new_callable=PropertyMock) as mock_location:
                mock_location.side_effect = GetLocationError()
                Move(obj_).execute()

    @staticmethod
    def test_get_velocity_error():
        obj_ = MovableStub(Point(1, 1), CartesianVelocity(0, 0))
        with pytest.raises(GetVelocityError):
            with patch.object(MovableStub, "velocity", new_callable=PropertyMock) as mock_velocity:
                mock_velocity.side_effect = GetVelocityError()
                Move(obj_).execute()

    @staticmethod
    def test_object_move_error():
        obj_ = MovableStub(Point(1, 1), CartesianVelocity(-2, -2))
        with pytest.raises(ObjectMoveError):
            with patch.object(Point, "move_to", new_callable=PropertyMock) as mock_move_to:
                mock_move_to.side_effect = ObjectMoveError()
                Move(obj_).execute()
