import logging
import math
import random
import time
import uuid
from pathlib import Path

import jwt
import pytest

import src.space_battle.game_server.routes as game_routes_module
from src.space_battle.config import settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction
from src.space_battle.core.init.register_game_dependencies import RegisterGameDependenciesAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Fuelable, Movable
from src.space_battle.core.server.game_router import game_router
from src.space_battle.game_server import game_runtime as game_runtime_module
from src.space_battle.game_server.app import app
from src.space_battle.game_server.game_runtime import get_game_runtime
from src.space_battle.utils.game_state_reporter import report_game_state

FIELD_SIZE = 100
DIRECTION_GRADATIONS = 8
SHIP_SPEED = 5
SHIP_FUEL = 100
FUEL_CONSUMPTION = 5
BUNKER_FUEL = 300
ASTEROID_SPEED_MIN = 2
ASTEROID_SPEED_MAX = 6
TICKS = 6
SIMULATION_STEP_SECONDS = 0.15
FINAL_DRAIN_SECONDS = 0.3

DEBUG_LOG_PATH = Path(__file__).resolve().parents[3] / "temp" / "e2e_game_state.log"

AGENT_1 = "agent-1"
AGENT_2 = "agent-2"
SHIP_1 = "ship-agent-1"
SHIP_2 = "ship-agent-2"
BUNKER_1 = "bunker-1"
BUNKER_2 = "bunker-2"
ASTEROID_1 = "asteroid-1"
ASTEROID_2 = "asteroid-2"


def _direction_theta(d: int, n: int = DIRECTION_GRADATIONS) -> float:
    return d / (n + 1) * 2 * math.pi


def _random_position(rng: random.Random, size: int = FIELD_SIZE) -> dict:
    return {"x": rng.randrange(size), "y": rng.randrange(size)}


def _ship_spec(rng: random.Random, obj_id: str, owner: str) -> dict:
    d = rng.randrange(DIRECTION_GRADATIONS)
    return {
        "id": obj_id,
        "type": "spaceship",
        "owner": owner,
        "properties": {
            "Movable.location": _random_position(rng),
            "Movable.velocity": {"r": SHIP_SPEED, "theta": _direction_theta(d)},
            "Rotatable.direction": {"d": d, "n": DIRECTION_GRADATIONS},
            "Rotatable.angular_velocity": 1,
            "Fuelable.fuel": SHIP_FUEL,
            "Fuelable.fuel_consumption": FUEL_CONSUMPTION,
        },
    }


def _fuel_bunker_spec(rng: random.Random, obj_id: str) -> dict:
    return {
        "id": obj_id,
        "type": "fuel_bunker",
        "capabilities": ["Fuelable", "Movable"],
        "properties": {
            "Movable.location": _random_position(rng),
            "Fuelable.fuel": BUNKER_FUEL,
        },
    }


def _asteroid_spec(rng: random.Random, obj_id: str) -> dict:
    d = rng.randrange(DIRECTION_GRADATIONS)
    return {
        "id": obj_id,
        "type": "asteroid",
        "capabilities": ["Movable", "Rotatable", "Destroyable"],
        "properties": {
            "Movable.location": _random_position(rng),
            "Movable.velocity": {
                "r": rng.randrange(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX),
                "theta": _direction_theta(d),
            },
            "Rotatable.direction": {"d": d, "n": DIRECTION_GRADATIONS},
            "Rotatable.angular_velocity": 0,
        },
    }


def build_initial_config(seed: int = 42) -> dict:
    """Сформировать initial-конфигурацию игры со случайными объектами на поле 100x100."""
    rng = random.Random(seed)
    return {
        "field": {"width": FIELD_SIZE, "height": FIELD_SIZE},
        "objects": [
            _ship_spec(rng, SHIP_1, AGENT_1),
            _ship_spec(rng, SHIP_2, AGENT_2),
            _fuel_bunker_spec(rng, BUNKER_1),
            _fuel_bunker_spec(rng, BUNKER_2),
            _asteroid_spec(rng, ASTEROID_1),
            _asteroid_spec(rng, ASTEROID_2),
        ],
    }


def _make_token(agent_id: str, game_id: str) -> str:
    return jwt.encode(
        {"sub": agent_id, "game_id": game_id, "exp": int(time.time()) + 3600},
        settings.secret_key,
        settings.algorithm,
    )


def _object_location(game, obj_id: str) -> tuple:
    movable = Ioc.resolve("Adapter", Movable, Movable, game.get_object(obj_id))
    return (movable.location.x, movable.location.y)


def _object_fuel(game, obj_id: str) -> int:
    fuelable = Ioc.resolve("Adapter", Fuelable, Fuelable, game.get_object(obj_id))
    return fuelable.fuel


def _send_command(client, token: str, agent_id: str, game_id: str, obj_id: str, action_id: str, data=None):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/message",
        json={
            "agent_id": agent_id,
            "game_id": game_id,
            "object_id": obj_id,
            "action_id": action_id,
            "data": data or {},
        },
        headers=headers,
    )
    assert response.status_code == 202
    assert response.json["status"] == "accepted"
    return response


class TestGameE2E:
    @staticmethod
    @pytest.fixture()
    def runtime(monkeypatch):
        RegisterGameDependenciesAction().execute()
        Ioc.resolve("IoC.Register", ActionBase, "Game", lambda *args: GameAction(*args)).execute()

        def _register_game(participants):
            return f"e2e-{uuid.uuid4()}"

        monkeypatch.setattr(game_routes_module, "register_game", _register_game)

        runtime = get_game_runtime()
        yield runtime

        runtime.stop()
        game_runtime_module._game_runtime = None
        game_router._games.clear()

    @staticmethod
    @pytest.fixture()
    def client():
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    @staticmethod
    def test_e2e_game_creation_movement_and_debug_report(runtime, client, caplog):
        """E2E: создание игры, старт, команды движения от двух агентов, отладочный вывод."""
        caplog.set_level(logging.DEBUG, logger=report_game_state.__module__)
        DEBUG_LOG_PATH.unlink(missing_ok=True)

        participants = [AGENT_1, AGENT_2]
        config = build_initial_config()

        create_response = client.post("/api/game/create", json={"participants": participants, "config": config})
        assert create_response.status_code == 201
        data = create_response.json["data"]
        game_id = data["game_id"]
        assert data["participants"] == participants

        game = game_router.get(game_id)
        assert game.field == {"width": FIELD_SIZE, "height": FIELD_SIZE}
        assert set(game.objects) == {SHIP_1, SHIP_2, BUNKER_1, BUNKER_2, ASTEROID_1, ASTEROID_2}

        initial_ships = {sid: _object_location(game, sid) for sid in (SHIP_1, SHIP_2)}
        initial_asteroids = {aid: _object_location(game, aid) for aid in (ASTEROID_1, ASTEROID_2)}
        initial_fuel = {sid: _object_fuel(game, sid) for sid in (SHIP_1, SHIP_2)}

        tokens = {agent: _make_token(agent, game_id) for agent in participants}
        ship_by_agent = {AGENT_1: SHIP_1, AGENT_2: SHIP_2}

        time.sleep(settings.game_tick_seconds * 2)

        for agent in participants:
            _send_command(client, tokens[agent], agent, game_id, ship_by_agent[agent], "Rotate")
        time.sleep(0.1)

        for _ in range(TICKS):
            for agent in participants:
                _send_command(client, tokens[agent], agent, game_id, ship_by_agent[agent], "MoveWithBurnFuel")
            time.sleep(SIMULATION_STEP_SECONDS)
            report_game_state(game, out=DEBUG_LOG_PATH)

        time.sleep(FINAL_DRAIN_SECONDS)

        final_ships = {sid: _object_location(game, sid) for sid in initial_ships}
        for sid, start in initial_ships.items():
            assert final_ships[sid] != start, f"Корабль {sid} не двигался: {start} == {final_ships[sid]}"

        final_fuel = {sid: _object_fuel(game, sid) for sid in initial_fuel}
        for sid, start in initial_fuel.items():
            expected_fuel = start - FUEL_CONSUMPTION * TICKS
            assert (
                final_fuel[sid] == expected_fuel
            ), f"Топливо корабля {sid} израсходовано неверно: {start} -> {final_fuel[sid]}, ожидалось {expected_fuel}"
            assert final_fuel[sid] >= 0

        final_asteroids = {aid: _object_location(game, aid) for aid in initial_asteroids}
        for aid, start in initial_asteroids.items():
            assert final_asteroids[aid] == start, f"Астероид {aid} сдвинулся: {start} -> {final_asteroids[aid]}"

        report_game_state(game, out=DEBUG_LOG_PATH)

        assert game_id in caplog.text

        assert DEBUG_LOG_PATH.exists()
        log_text = DEBUG_LOG_PATH.read_text(encoding="utf-8")
        assert game_id in log_text
        for obj_id in (SHIP_1, SHIP_2, BUNKER_1, BUNKER_2, ASTEROID_1, ASTEROID_2):
            assert obj_id in log_text
