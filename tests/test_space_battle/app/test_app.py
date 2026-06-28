import threading
from queue import Queue

import pytest

from src.space_battle.app.app import app
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, SchedulerAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.actions import UseSchedulerAction
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.server_thread import ServerThread


class TestApp:
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

        game = Ioc.resolve("Game", GameAction, 0.05, scheduler)

        game_router.register(game)
        server_thread.queue.put(game)

        server_thread.run()

        msg = {
            "agent_id": "agent_1",
            "game_id": game.id,
            "object_id": "object_1",
            "action_id": "StubAction",
            "data": {"msg": "act1"},
        }
        response = client.post(
            "http://localhost:5000/api/message", json=msg, headers={"Content-Type": "application/json"}
        )

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
