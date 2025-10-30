import pytest

from src.space_battle.core.base import Movable
from src.space_battle.entities.actions import Move
from src.space_battle.entities.spaceship import Spaceship
from src.space_battle.models.vector import CartesianVector, Point


class TestMove:
    @staticmethod
    @pytest.mark.parametrize("obj_", [Spaceship(Point(12, 5), CartesianVector(-7, 3))])
    def test_move(obj_: Movable):
        Move(obj_).execute()
        assert obj_.location == CartesianVector(5, 8)
