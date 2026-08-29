import threading
from queue import Queue

import jwt
import pytest

from src.space_battle.auth_service.app import app as auth_app
from src.space_battle.auth_service.app import games_db
from src.space_battle.auth_service.models import GameRequestModel, TokenRequestModel
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, SchedulerAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.actions import UseSchedulerAction
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.server_thread import ServerThread
from src.space_battle.game_server.app import app as game_app
from src.space_battle.game_server.models import AgentMessageModel


class TestAuthService:
    @staticmethod
    @pytest.fixture(autouse=True)
    def clean_db():
        games_db.clear()
        yield
        games_db.clear()

    @staticmethod
    @pytest.fixture
    def auth_client():
        with auth_app.test_client() as client:
            yield client

    @staticmethod
    @pytest.fixture
    def game_client():
        with game_app.test_client() as client:
            yield client

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
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        Ioc.resolve("IoC.Register", ActionBase, "Game", lambda *args: GameAction(*args)).execute()

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

    @staticmethod
    def test_full_authorization_flow(server_thread_fixture, auth_client, game_client):
        scheduler = SchedulerAction()
        server_thread = server_thread_fixture(Queue())
        server_thread.queue.put(UseSchedulerAction(server_thread, scheduler))
        server_thread.run()

        request = GameRequestModel(participants=["user_1", "user_2"])
        response = auth_client.post("/game", json=request.model_dump())
        assert response.status_code == 201
        game_id = response.get_json()["data"]["game_id"]

        game = Ioc.resolve("Game", GameAction, 0.05, scheduler, {"id": game_id})
        game_router.register(game)
        server_thread.queue.put(game)

        request = TokenRequestModel(
            user_id="user_1",
            game_id=game_id,
        )
        response = auth_client.post("/auth/token", json=request.model_dump())
        assert response.status_code == 200
        token = response.get_json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        request = AgentMessageModel(
            agent_id="agent_1",
            game_id=game_id,
            object_id="object_1",
            action_id="StubAction",
            data={"msg": "act1"},
        )
        response = game_client.post(
            "/api/message",
            json=request.model_dump(),
            headers=headers,
        )
        assert response.status_code == 202
        assert response.json["status"] == "accepted"

    @staticmethod
    def test_unauthorized_user_cannot_get_token(auth_client):
        request = GameRequestModel(participants=["user_1"])
        response = auth_client.post("/game", json=request.model_dump())
        game_id = response.get_json()["data"]["game_id"]

        request = TokenRequestModel(
            user_id="user_2",
            game_id=game_id,
        )
        response = auth_client.post("/auth/token", json=request.model_dump())
        assert response.status_code == 403

    @staticmethod
    def test_token_from_another_game_is_rejected(auth_client, game_client):
        request = GameRequestModel(participants=["user_1"])
        response = auth_client.post("/game", json=request.model_dump())
        game_id_1 = response.get_json()["data"]["game_id"]

        request = GameRequestModel(participants=["user_2"])
        response = auth_client.post("/game", json=request.model_dump())
        game_id_2 = response.get_json()["data"]["game_id"]

        request = TokenRequestModel(
            user_id="user_1",
            game_id=game_id_1,
        )
        response = auth_client.post("/auth/token", json=request.model_dump())
        token_1 = response.json["data"]["access_token"]

        headers = {"Authorization": f"Bearer {token_1}"}
        request = AgentMessageModel(
            agent_id="agent_2",
            game_id=game_id_2,
            object_id="object_2",
            action_id="StubAction",
            data={"msg": "act2"},
        )
        response = game_client.post(
            "/api/message",
            json=request.model_dump(),
            headers=headers,
        )
        assert response.status_code == 403
        assert response.json["status"] == "error"

    @staticmethod
    def test_invalid_token_signature(auth_client, game_client):
        request = GameRequestModel(participants=["user_1"])
        response = auth_client.post("/game", json=request.model_dump())
        game_id = response.get_json()["data"]["game_id"]

        fake_token = jwt.encode(
            {"sub": "user_1", "game_id": game_id},
            "wrong_secret",
            algorithm="HS256",
        )

        headers = {"Authorization": f"Bearer {fake_token}"}
        request = AgentMessageModel(
            agent_id="agent_1",
            game_id=game_id,
            object_id="object_1",
            action_id="StubAction",
            data={"msg": "act1"},
        )
        response = game_client.post(
            "/api/message",
            json=request.model_dump(),
            headers=headers,
        )
        assert response.status_code == 401
