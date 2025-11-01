from unittest.mock import PropertyMock, patch

import pytest

from space_battle.core.exceptions import (
    GetAngularVelocityError,
    GetDirectionError,
    GetLocationError,
    GetVelocityError,
    ObjectMoveError,
    ObjectRotateError,
)
from src.space_battle.core.base import Movable, Rotatable
from src.space_battle.core.space import CartesianVelocity, Direction, Point, VectorBase
from src.space_battle.entities.actions import Move, Rotate


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


class RotatableStub(Rotatable):
    def __init__(self, direction: Direction, angular_velocity: int):
        self._direction = direction
        self._angular_velocity = angular_velocity

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction):
        self._direction = direction

    @property
    def angular_velocity(self) -> int:
        return self._angular_velocity


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


class TestRotate:
    @staticmethod
    @pytest.mark.parametrize(
        "obj_",
        [
            RotatableStub(Direction(2, 255), 3),
            RotatableStub(Direction(2, 255), 258),
            RotatableStub(Direction(2, 255), -252),
            RotatableStub(Direction(-2, 255), 7),
            RotatableStub(Direction(-2, 255), -248),
        ],
    )
    def test_rotate(obj_: Rotatable):
        Rotate(obj_).execute()
        assert obj_.direction == Direction(5, 255)

    @staticmethod
    @pytest.mark.parametrize(
        "obj_",
        [
            RotatableStub(Direction(2, 255), 0),
            RotatableStub(Direction(2, 255), 255),
        ],
    )
    def test_rotate_in_place(obj_: Rotatable):
        Rotate(obj_).execute()
        assert obj_.direction == Direction(2, 255)

    @staticmethod
    def test_get_direction_error():
        obj_ = RotatableStub(Direction(2, 255), 3)
        with pytest.raises(GetDirectionError):
            with patch.object(RotatableStub, "direction", new_callable=PropertyMock) as mock_direction:
                mock_direction.side_effect = GetDirectionError()
                Rotate(obj_).execute()

    @staticmethod
    def test_get_angular_velocity_error():
        obj_ = RotatableStub(Direction(2, 255), 3)
        with pytest.raises(GetAngularVelocityError):
            with patch.object(RotatableStub, "angular_velocity", new_callable=PropertyMock) as mock_angular_velocity:
                mock_angular_velocity.side_effect = GetAngularVelocityError()
                Rotate(obj_).execute()

    @staticmethod
    def test_object_move_error():
        obj_ = RotatableStub(Direction(2, 255), 3)
        with pytest.raises(ObjectRotateError):
            with patch.object(Direction, "rotate_by", new_callable=PropertyMock) as mock_rotate_by:
                mock_rotate_by.side_effect = ObjectRotateError()
                Rotate(obj_).execute()
