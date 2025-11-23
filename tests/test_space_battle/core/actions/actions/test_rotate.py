from unittest.mock import PropertyMock, patch

import pytest

from src.space_battle.core.actions.actions import Rotate
from src.space_battle.core.base import Rotatable
from src.space_battle.core.exceptions import (
    GetAngularVelocityError,
    GetDirectionError,
    ObjectRotateError,
)
from src.space_battle.core.space import Direction
from tests.test_space_battle.core import RotatableStub


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
