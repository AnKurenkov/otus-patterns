import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.init.game_init_exception import GameInitError
from src.space_battle.core.init.game_init_value_parser import parse_value
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.space import Direction, Point, PolarVelocity


class TestGameInitValueParser:
    @staticmethod
    def test_scalars_passthrough():
        assert parse_value(5) == 5
        assert parse_value(3.14) == 3.14
        assert parse_value("abc") == "abc"
        assert parse_value(True) is True

    @staticmethod
    def test_point_schema():
        assert parse_value({"x": 1, "y": 2}) == Point(1, 2)

    @staticmethod
    def test_polar_velocity_schema():
        assert parse_value({"r": 3, "theta": 1.0}) == PolarVelocity(3, 1.0)

    @staticmethod
    def test_direction_schema():
        assert parse_value({"d": 1, "n": 8}) == Direction(1, 8)

    @staticmethod
    def test_typed_value_known_type():
        assert parse_value({"type": "Point", "value": {"x": 10, "y": 20}}) == Point(10, 20)

    @staticmethod
    def test_typed_value_from_ioc():
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Game.Init.Value.custom",
            lambda *args: lambda raw: {"custom": raw},
        ).execute()
        assert parse_value({"type": "custom", "value": 42}) == {"custom": 42}

    @staticmethod
    def test_unknown_schema_raises():
        with pytest.raises(GameInitError):
            parse_value({"foo": 1})

    @staticmethod
    def test_unknown_typed_value_raises():
        with pytest.raises(GameInitError):
            parse_value({"type": "unknown_type", "value": 1})
