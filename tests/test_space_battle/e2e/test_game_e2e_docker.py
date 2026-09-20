import json
import os
import shutil
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest
import requests

from src.space_battle.config import settings
from tests.test_space_battle.e2e.test_game_e2e import (
    AGENT_1,
    AGENT_2,
    ASTEROID_1,
    ASTEROID_2,
    BUNKER_1,
    BUNKER_2,
    FIELD_SIZE,
    FINAL_DRAIN_SECONDS,
    FUEL_CONSUMPTION,
    SHIP_1,
    SHIP_2,
    SIMULATION_STEP_SECONDS,
    TICKS,
    build_initial_config,
)

pytestmark = pytest.mark.docker

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
COMPOSE_E2E_FILE = Path(__file__).resolve().parent / "docker-compose.e2e.yml"

DEBUG_LOG_PATH = REPO_ROOT / "temp" / "e2e_game_state_docker.log"

GAME_PORT = int(os.environ.get("SPACE_BATTLE_GAME_SERVICE_TEST_PORT", "18001"))
AUTH_PORT = int(os.environ.get("SPACE_BATTLE_AUTH_SERVICE_TEST_PORT", "18002"))

READY_TIMEOUT = 180
FINAL_STATE_TIMEOUT = 15


def _compose_cmd(*args) -> list:
    return ["docker", "compose", "-f", str(COMPOSE_FILE), "-f", str(COMPOSE_E2E_FILE), *args]


def _compose_env() -> dict:
    env = dict(os.environ)
    # Базовые порты из .env (.env.example) совпадают с тестовыми, чтобы
    # port-mapping в docker-compose.yml и override не задваивались.
    env["SPACE_BATTLE_AUTH_SERVICE_PORT"] = str(AUTH_PORT)
    env["SPACE_BATTLE_GAME_SERVICE_PORT"] = str(GAME_PORT)
    return env


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=20,
        )
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _port_is_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _wait_for_ports(timeout: int = READY_TIMEOUT) -> None:
    auth = f"http://127.0.0.1:{AUTH_PORT}"
    game = f"http://127.0.0.1:{GAME_PORT}"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        tcp_ok = all(_port_is_busy(p) for p in (AUTH_PORT, GAME_PORT))
        # Проверка HTTP-готовности: Flask может принять TCP-коннект раньше,
        # чем начнёт обрабатывать запросы, и тогда первый запрос обрывается.
        http_ok = _http_probe(f"{auth}/auth/token") and _http_probe(f"{game}/api/message")
        if tcp_ok and http_ok:
            return
        time.sleep(2)
    raise RuntimeError(f"Сервисы не поднялись за {timeout} на портах: auth={AUTH_PORT}, game={GAME_PORT}.")


def _http_probe(url: str) -> bool:
    try:
        response = requests.post(url, json={}, timeout=5)
    except requests.RequestException:
        return False
    return response.status_code in (400, 401, 404)


@pytest.fixture(scope="session")
def docker_services() -> dict:
    """Поднимает auth_service и game_server в Docker и возвращает их базовые URL."""
    if not _docker_available():
        pytest.skip("Docker (compose + daemon) недоступен: пропускаем Docker E2E-тесты.")

    for port in (AUTH_PORT, GAME_PORT):
        if _port_is_busy(port):
            pytest.skip(f"Тестовый порт {port} занят: пропускаем Docker E2E-тесты.")

    base_urls = {
        "auth": f"http://127.0.0.1:{AUTH_PORT}",
        "game": f"http://127.0.0.1:{GAME_PORT}",
    }

    startup = subprocess.run(
        _compose_cmd("up", "-d", "--build", "auth_service", "game_server"),
        cwd=str(REPO_ROOT),
        env=_compose_env(),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if startup.returncode != 0:
        raise RuntimeError(f"docker compose up завершился с ошибкой:\n{startup.stdout}\n{startup.stderr}")

    try:
        _wait_for_ports()
        yield base_urls
    finally:
        subprocess.run(
            _compose_cmd("down", "--remove-orphans", "-v", "--timeout", "10"),
            cwd=str(REPO_ROOT),
            env=_compose_env(),
            capture_output=True,
            text=True,
            timeout=120,
        )


def _api_post(url: str, token: str | None, payload: dict, expected_status: int):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    attempts = 5
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        except requests.ConnectionError as e:
            last_error = e
            time.sleep(0.5 * (attempt + 1))
            continue
        if response.status_code != expected_status:
            raise AssertionError(f"{url}: {response.status_code} {response.text}")
        return response
    raise AssertionError(f"POST {url} не выполнен после {attempts} попыток: {last_error}")


def _send_command(game_url: str, token: str, agent_id: str, game_id: str, obj_id: str, action_id: str):
    response = _api_post(
        f"{game_url}/api/message",
        token,
        {
            "agent_id": agent_id,
            "game_id": game_id,
            "object_id": obj_id,
            "action_id": action_id,
            "data": {},
        },
        expected_status=202,
    )
    assert response.json()["status"] == "accepted"


def _fetch_state(game_url: str, token: str, game_id: str) -> dict:
    response = _api_post(
        f"{game_url}/api/game/state",
        token,
        {"game_id": game_id, "agent_id": AGENT_1},
        expected_status=200,
    )
    assert response.json()["status"] == "ok"
    return response.json()["data"]


def _obj_state(state: dict, obj_id: str) -> dict:
    for obj in state["objects"]:
        if obj["id"] == obj_id:
            return obj
    raise KeyError(f"Object {obj_id} not found in state")


def _location(obj_state: dict) -> tuple:
    return obj_state["location"]["x"], obj_state["location"]["y"]


def _fuel(obj_state: dict) -> int:
    return obj_state["fuel"]


def _write_log_entry(state: dict) -> None:
    DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_line = f"[{datetime.now().isoformat(timespec='seconds')}]\n{json.dumps(state, ensure_ascii=False, default=str)}"
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(log_line + "\n")


def _wait_for(predicate, timeout: int):
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            if predicate():
                return
        except AssertionError as e:
            last_error = e
        except Exception as e:  # noqa: BLE001
            last_error = e
        time.sleep(0.2)
    raise AssertionError(f"Условие не выполнилось за {timeout} с: {last_error}")


def test_docker_e2e_game_creation_movement_and_debug_report(docker_services):
    """E2E в Docker: создание игры (реальный вызов auth_service), JWT, движение, отладочный вывод."""
    auth_url = docker_services["auth"]
    game_url = docker_services["game"]

    participants = [AGENT_1, AGENT_2]
    config = build_initial_config()

    create_response = _api_post(
        f"{game_url}/api/game/create",
        None,
        {"participants": participants, "config": config},
        expected_status=201,
    )
    data = create_response.json()["data"]
    game_id = data["game_id"]
    assert data["participants"] == participants

    tokens: dict[str, str] = {}
    for agent in participants:
        token_response = _api_post(
            f"{auth_url}/auth/token",
            None,
            {"user_id": agent, "game_id": game_id},
            expected_status=200,
        )
        tokens[agent] = token_response.json()["data"]["access_token"]

    def _state_ready() -> bool:
        state = _fetch_state(game_url, tokens[AGENT_1], game_id)
        return state["field"] == {"width": FIELD_SIZE, "height": FIELD_SIZE} and {
            obj["id"] for obj in state["objects"]
        } == {SHIP_1, SHIP_2, BUNKER_1, BUNKER_2, ASTEROID_1, ASTEROID_2}

    _wait_for(_state_ready, timeout=30)

    state = _fetch_state(game_url, tokens[AGENT_1], game_id)
    initial_ships = {sid: _location(_obj_state(state, sid)) for sid in (SHIP_1, SHIP_2)}
    initial_asteroids = {aid: _location(_obj_state(state, aid)) for aid in (ASTEROID_1, ASTEROID_2)}
    initial_fuel = {sid: _fuel(_obj_state(state, sid)) for sid in (SHIP_1, SHIP_2)}

    ship_by_agent = {AGENT_1: SHIP_1, AGENT_2: SHIP_2}

    time.sleep(settings.game_tick_seconds * 2)

    for agent in participants:
        _send_command(game_url, tokens[agent], agent, game_id, ship_by_agent[agent], "Rotate")
    time.sleep(0.1)

    DEBUG_LOG_PATH.unlink(missing_ok=True)

    for _ in range(TICKS):
        for agent in participants:
            _send_command(game_url, tokens[agent], agent, game_id, ship_by_agent[agent], "MoveWithBurnFuel")
        time.sleep(SIMULATION_STEP_SECONDS)
        _write_log_entry(_fetch_state(game_url, tokens[AGENT_1], game_id))

    time.sleep(FINAL_DRAIN_SECONDS)

    def _final_fuel_reached() -> bool:
        final_state = _fetch_state(game_url, tokens[AGENT_1], game_id)
        final_fuel = {sid: _fuel(_obj_state(final_state, sid)) for sid in initial_fuel}
        return all(final_fuel[sid] == initial_fuel[sid] - FUEL_CONSUMPTION * TICKS for sid in initial_fuel)

    _wait_for(_final_fuel_reached, timeout=FINAL_STATE_TIMEOUT)

    final_state = _fetch_state(game_url, tokens[AGENT_1], game_id)
    final_ships = {sid: _location(_obj_state(final_state, sid)) for sid in initial_ships}
    for sid, start in initial_ships.items():
        assert final_ships[sid] != start, f"Корабль {sid} не двигался: {start} == {final_ships[sid]}"

    final_fuel = {sid: _fuel(_obj_state(final_state, sid)) for sid in initial_fuel}
    for sid, start in initial_fuel.items():
        expected_fuel = start - FUEL_CONSUMPTION * TICKS
        assert (
            final_fuel[sid] == expected_fuel
        ), f"Топливо корабля {sid} израсходовано неверно: {start} -> {final_fuel[sid]}, ожидалось {expected_fuel}"
        assert final_fuel[sid] >= 0

    final_asteroids = {aid: _location(_obj_state(final_state, aid)) for aid in initial_asteroids}
    for aid, start in initial_asteroids.items():
        assert final_asteroids[aid] == start, f"Астероид {aid} сдвинулся: {start} -> {final_asteroids[aid]}"

    _write_log_entry(final_state)

    assert DEBUG_LOG_PATH.exists()
    log_text = DEBUG_LOG_PATH.read_text(encoding="utf-8")
    assert game_id in log_text
    for obj_id in (SHIP_1, SHIP_2, BUNKER_1, BUNKER_2, ASTEROID_1, ASTEROID_2):
        assert obj_id in log_text
