import threading
import time
import uuid
from queue import Queue

import jwt
import pytest

import src.space_battle.game_server.app as game_app_module
from src.space_battle.config import settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, SchedulerAction
from src.space_battle.core.init.init_object_factories import RegisterGameObjectFactoriesInitAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.actions import UseSchedulerAction
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.server_thread import ServerThread
from src.space_battle.game_server.app import app
from src.space_battle.game_server.auth_client import AuthServiceError


class TestGameServer:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        class StubAction(ActionBase):
            def __init__(self, obj, msg):
                self._obj = obj
                self._msg = msg

            def execute(self):
                print(self._msg)

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubAction",
            lambda obj, msg: StubAction(obj, msg),
        ).execute()

        class StubEventAction(ActionBase):
            def __init__(self, event: threading.Event):
                self._event = event

            def execute(self):
                self._event.set()

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubEventAction",
            lambda event: StubEventAction(event),
        ).execute()

        RegisterGameObjectFactoriesInitAction().execute()

    @staticmethod
    @pytest.fixture()
    def server_thread_fixture():
        server_thread: ServerThread | None = None

        def _create(queue):
            nonlocal server_thread
            server_thread = ServerThread(queue)
            return server_thread

        yield _create

        if server_thread:
            server_thread.stop()

    @staticmethod
    @pytest.fixture
    def client():
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    @staticmethod
    def test_app_message(capsys, server_thread_fixture, client):
        scheduler = SchedulerAction()
        server_thread = server_thread_fixture(Queue())
        server_thread.queue.put(UseSchedulerAction(server_thread, scheduler))

        Ioc.resolve("IoC.Register", ActionBase, "Game", lambda *args: GameAction(*args)).execute()

        game_id = str(uuid.uuid4())
        initial = {
            "id": game_id,
            "objects": [{"id": "object_1", "type": "spaceship", "owner": "agent_1"}],
        }
        game = Ioc.resolve("Game", GameAction, 0.05, scheduler, initial)

        game_router.register(game)
        server_thread.queue.put(game)

        server_thread.run()

        token = jwt.encode(
            {"game_id": game.id, "sub": "agent_1", "exp": int(time.time()) + 3600},
            settings.secret_key,
            settings.algorithm,
        )
        headers = {"Authorization": f"Bearer {token}"}
        msg = {
            "agent_id": "agent_1",
            "game_id": game.id,
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {"msg": "act1"},
        }
        response = client.post("/api/message", json=msg, headers=headers)

        assert response.status_code == 202
        assert response.json["status"] == "accepted"
        assert response.json["data"]["game_id"] == game.id
        assert response.json["data"]["object_id"] == "object_1"
        assert response.json["data"]["action_id"] == "StubAction"

        event = threading.Event()
        server_thread.queue.put(Ioc.resolve("StubEventAction", ActionBase, event))
        assert event.wait(timeout=5)

        out = capsys.readouterr().out
        assert "act1" in out

    @staticmethod
    def test_missing_auth_header_returns_401(client):
        msg = {
            "agent_id": "agent_1",
            "game_id": "game-1",
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {},
        }
        response = client.post("/api/message", json=msg)
        assert response.status_code == 401
        assert response.json["status"] == "error"
        assert response.json["message"] == "Invalid authorization header."

    @staticmethod
    def test_expired_token_returns_401(client):
        token = jwt.encode(
            {"game_id": "game-1", "exp": int(time.time()) - 3600},
            settings.secret_key,
            settings.algorithm,
        )
        headers = {"Authorization": f"Bearer {token}"}
        msg = {
            "agent_id": "agent_1",
            "game_id": "game-1",
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {},
        }
        response = client.post("/api/message", json=msg, headers=headers)
        assert response.status_code == 401
        assert response.json["message"] == "Token has expired."

    @staticmethod
    def test_missing_game_returns_processing_error_404(client):
        token = jwt.encode(
            {"game_id": "unknown-game", "sub": "agent_1", "exp": int(time.time()) + 3600},
            settings.secret_key,
            settings.algorithm,
        )
        headers = {"Authorization": f"Bearer {token}"}
        msg = {
            "agent_id": "agent_1",
            "game_id": "unknown-game",
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {},
        }
        response = client.post("/api/message", json=msg, headers=headers)
        assert response.status_code == 404
        assert response.json["status"] == "error"

    @staticmethod
    def test_agent_id_not_matching_token_sub_returns_403(client):
        token = jwt.encode(
            {"game_id": "game-1", "sub": "agent_1", "exp": int(time.time()) + 3600},
            settings.secret_key,
            settings.algorithm,
        )
        headers = {"Authorization": f"Bearer {token}"}
        msg = {
            "agent_id": "agent_2",
            "game_id": "game-1",
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {},
        }
        response = client.post("/api/message", json=msg, headers=headers)
        assert response.status_code == 403
        assert response.json["status"] == "error"
        assert response.json["message"] == "Agent ID does not match token subject."

    @staticmethod
    def test_create_game_registers_in_router(monkeypatch, client):
        monkeypatch.setattr(game_app_module, "register_game", lambda participants: "game-http-1")
        response = client.post("/api/game/create", json={"participants": ["user_1", "user_2"]})
        assert response.status_code == 201
        assert response.json["status"] == "created"
        assert response.json["data"]["game_id"] == "game-http-1"

        game = game_router.get("game-http-1")
        assert game.id == "game-http-1"

    @staticmethod
    def test_create_game_auth_error_returns_502(monkeypatch, client):
        def _fail(participants):
            raise AuthServiceError("Auth Service is down.")

        monkeypatch.setattr(game_app_module, "register_game", _fail)
        response = client.post("/api/game/create", json={"participants": ["user_1"]})
        assert response.status_code == 502
        assert response.json["status"] == "error"
        assert "Auth Service" in response.json["message"]

    @staticmethod
    def test_create_game_with_empty_body_returns_400(client):
        response = client.post("/api/game/create", json={})
        assert response.status_code == 400
        assert response.json["status"] == "error"
