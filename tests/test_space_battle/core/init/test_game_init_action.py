import json

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, GameInitAction, SchedulerAction
from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.fuelable_adapter_actions import IocRegisterFuelableAction
from src.space_battle.core.adapters.actions.movable_adapter_actions import IocRegisterMovableAction
from src.space_battle.core.adapters.actions.rotatable_adapter_actions import IocRegisterRotatableAction
from src.space_battle.core.exceptions.exceptions import ObjectCapabilityError
from src.space_battle.core.init.game_init_exception import GameInitError
from src.space_battle.core.init.game_init_loader import load_initial_from_json
from src.space_battle.core.init.init_object_factories import RegisterGameObjectFactoriesInitAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities.fuelable import Fuelable
from src.space_battle.core.objects.capabilities.movable import Movable
from src.space_battle.core.objects.capabilities.rotatable import Rotatable
from src.space_battle.core.objects.fuel_bunker import FuelBunker
from src.space_battle.core.objects.game_object_base import GameObjectBase
from src.space_battle.core.objects.space_ship import SpaceShip
from src.space_battle.core.space import Point, PolarVelocity

GAME_OBJECTS: dict = {}


class TestGameInitAction:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        IocRegisterMovableAction().execute()
        IocRegisterRotatableAction().execute()
        IocRegisterFuelableAction().execute()
        IocRegisterCreateAdapterAction().execute()
        RegisterGameObjectFactoriesInitAction().execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game.Objects", lambda: GAME_OBJECTS).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Game.Init.Object.custom_object",
            lambda obj_id: GameObjectBase(obj_id, "custom_object", {"Movable"}),
        ).execute()

    @pytest.fixture(autouse=True)
    def fresh_game_objects(self):
        GAME_OBJECTS.clear()
        yield

    @staticmethod
    def test_init_none_is_noop():
        GameInitAction(None).execute()

    @staticmethod
    def test_create_spaceship_and_read_properties():
        initial = {
            "version": 1,
            "id": "game-1",
            "field": {"width": 100, "height": 100},
            "objects": [
                {
                    "id": "ship-1",
                    "type": "spaceship",
                    "properties": {
                        "Movable.location": {"x": 1, "y": 2},
                        "Movable.velocity": {"r": 3, "theta": 1.0},
                        "Rotatable.direction": {"d": 1, "n": 8},
                        "Rotatable.angular_velocity": 2,
                        "Fuelable.fuel": 100,
                        "Fuelable.fuel_consumption": 5,
                    },
                }
            ],
        }

        GameInitAction(initial).execute()

        objects = Ioc.resolve("Game.Objects", dict)
        ship = objects["ship-1"]
        assert isinstance(ship, SpaceShip)
        assert Ioc.resolve("Game.Field", dict) == {"width": 100, "height": 100}

        movable = Ioc.resolve("Adapter", Movable, Movable, ship)
        rotatable = Ioc.resolve("Adapter", Rotatable, Rotatable, ship)
        fuelable = Ioc.resolve("Adapter", Fuelable, Fuelable, ship)
        assert movable.location == Point(1, 2)
        assert movable.velocity == PolarVelocity(3, 1.0)
        assert rotatable.direction.d == 1
        assert rotatable.direction.n == 8
        assert rotatable.angular_velocity == 2
        assert fuelable.fuel == 100
        assert fuelable.fuel_consumption == 5

    @staticmethod
    def test_create_multiple_object_types():
        initial = {
            "id": "game-2",
            "objects": [
                {"id": "ship-1", "type": "spaceship", "properties": {"Movable.location": {"x": 0, "y": 0}}},
                {"id": "bunker-1", "type": "fuel_bunker", "properties": {"Fuelable.fuel": 500}},
                {"id": "asteroid-1", "type": "asteroid", "properties": {"Movable.location": {"x": 10, "y": 10}}},
            ],
        }

        GameInitAction(initial).execute()

        objects = Ioc.resolve("Game.Objects", dict)
        assert "ship-1" in objects
        assert "bunker-1" in objects
        assert "asteroid-1" in objects
        assert isinstance(objects["bunker-1"], FuelBunker)

    @staticmethod
    def test_unsupported_version_raises():
        initial = {"version": 2, "id": "game-1", "objects": []}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_missing_game_id_raises():
        initial = {"objects": []}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_missing_object_id_raises():
        initial = {"id": "game-1", "objects": [{"type": "spaceship"}]}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_duplicate_object_id_raises():
        initial = {
            "id": "game-1",
            "objects": [
                {"id": "obj-1", "type": "spaceship"},
                {"id": "obj-1", "type": "spaceship"},
            ],
        }
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_unknown_object_type_raises():
        initial = {"id": "game-1", "objects": [{"id": "obj-1", "type": "ufo"}]}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_unknown_capability_raises():
        initial = {
            "id": "game-1",
            "objects": [{"id": "ship-1", "type": "spaceship", "properties": {"Shootable.location": {"x": 1, "y": 1}}}],
        }
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_unknown_value_schema_raises():
        initial = {
            "id": "game-1",
            "objects": [{"id": "ship-1", "type": "spaceship", "properties": {"Movable.location": {"q": 1}}}],
        }
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_objects_not_a_list_raises():
        initial = {"id": "game-1", "objects": "spaceships"}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_object_spec_not_a_dict_raises():
        initial = {"id": "game-1", "objects": [42]}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_object_missing_type_raises():
        initial = {"id": "game-1", "objects": [{"id": "obj-1"}]}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_field_not_a_dict_raises():
        initial = {"id": "game-1", "field": "field_data", "objects": []}
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_property_without_capability_dot_raises():
        initial = {
            "id": "game-1",
            "objects": [{"id": "ship-1", "type": "spaceship", "properties": {"MovableLocation": {"x": 0, "y": 0}}}],
        }
        with pytest.raises(GameInitError):
            GameInitAction(initial).execute()

    @staticmethod
    def test_custom_object_factory():
        initial = {
            "id": "game-1",
            "objects": [
                {
                    "id": "custom-1",
                    "type": "custom_object",
                    "properties": {"Movable.location": {"x": 7, "y": 8}},
                }
            ],
        }

        GameInitAction(initial).execute()

        obj = Ioc.resolve("Game.Objects", dict)["custom-1"]
        assert isinstance(obj, GameObjectBase)
        movable = Ioc.resolve("Adapter", Movable, Movable, obj)
        assert movable.location == Point(7, 8)

    @staticmethod
    def test_capabilities_override():
        initial = {
            "id": "game-1",
            "objects": [
                {
                    "id": "ship-1",
                    "type": "spaceship",
                    "capabilities": ["Movable"],
                    "properties": {"Movable.location": {"x": 0, "y": 0}},
                }
            ],
        }

        GameInitAction(initial).execute()

        obj = Ioc.resolve("Game.Objects", dict)["ship-1"]
        assert obj.capabilities == {"Movable"}
        with pytest.raises(ObjectCapabilityError):
            Ioc.resolve("Adapter", Rotatable, Rotatable, obj)

    @staticmethod
    def test_game_action_wiring_and_get_object():
        initial = {
            "id": "game-1",
            "objects": [{"id": "ship-1", "type": "spaceship", "properties": {"Movable.location": {"x": 5, "y": 5}}}],
        }

        game = GameAction(0.05, SchedulerAction(), initial)

        ship = game.get_object("ship-1")
        assert isinstance(ship, SpaceShip)
        movable = Ioc.resolve("Adapter", Movable, Movable, ship)
        assert movable.location == Point(5, 5)

    @staticmethod
    def test_game_init_from_json_file(tmp_path):
        initial = {
            "id": "game-e2e",
            "objects": [
                {
                    "id": "ship-1",
                    "type": "spaceship",
                    "properties": {
                        "Movable.location": {"x": 1, "y": 1},
                        "Rotatable.direction": {"d": 2, "n": 8},
                    },
                },
                {"id": "bunker-1", "type": "fuel_bunker", "properties": {"Fuelable.fuel": 300}},
            ],
        }
        file = tmp_path / "initial.json"
        file.write_text(json.dumps(initial), encoding="utf-8")

        game = GameAction(0.05, SchedulerAction(), load_initial_from_json(file))

        assert isinstance(game.get_object("ship-1"), SpaceShip)
        assert isinstance(game.get_object("bunker-1"), FuelBunker)
        rotatable = Ioc.resolve("Adapter", Rotatable, Rotatable, game.get_object("ship-1"))
        assert rotatable.direction.d == 2
