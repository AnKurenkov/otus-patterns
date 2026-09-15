import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, SchedulerAction
from src.space_battle.core.actions.guard_action import GuardAction
from src.space_battle.core.init.init_object_factories import RegisterGameObjectFactoriesInitAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.interpret_action import InterpretAction
from src.space_battle.game_server.models import AgentMessageModel


class PrintAction(ActionBase):
    def __init__(self, obj, data):
        self._obj = obj
        self._data = data

    def execute(self):
        print(self._data.get("msg", ""))


class TestInterpretAction:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "PrintAction",
            lambda obj, data: PrintAction(obj, data),
        ).execute()
        RegisterGameObjectFactoriesInitAction().execute()

    @pytest.fixture()
    def game(self):
        initial = {
            "id": "game-1",
            "objects": [
                {"id": "ship-1", "type": "spaceship", "owner": "user_1"},
                {"id": "asteroid-1", "type": "asteroid"},
            ],
        }
        g = GameAction(0.05, SchedulerAction(), initial)
        game_router.register(g)
        return g

    @staticmethod
    def _drain(game):
        items = []
        while not game.queue.empty():
            items.append(game.queue.get(block=False))
        return items

    def test_wraps_action_in_guard(self, game):
        msg = AgentMessageModel(
            agent_id="user_1", game_id="game-1", object_id="ship-1", action_id="PrintAction", data={"msg": "go"}
        )

        InterpretAction(msg, agent_id="user_1").execute()

        items = self._drain(game)
        assert len(items) == 1
        assert isinstance(items[0], GuardAction)

    def test_allowed_command_executes(self, game, capsys):
        msg = AgentMessageModel(
            agent_id="user_1", game_id="game-1", object_id="ship-1", action_id="PrintAction", data={"msg": "go"}
        )

        InterpretAction(msg, agent_id="user_1").execute()
        guard = game.queue.get(block=False)
        guard.execute()

        out = capsys.readouterr().out
        assert "go" in out

    def test_denied_command_ignored(self, game, capsys):
        msg = AgentMessageModel(
            agent_id="user_2", game_id="game-1", object_id="ship-1", action_id="PrintAction", data={"msg": "no"}
        )

        InterpretAction(msg, agent_id="user_2").execute()
        guard = game.queue.get(block=False)
        guard.execute()

        out = capsys.readouterr().out
        assert "no" not in out

    def test_unowned_object_ignored(self, game, capsys):
        msg = AgentMessageModel(
            agent_id="user_1", game_id="game-1", object_id="asteroid-1", action_id="PrintAction", data={"msg": "no"}
        )

        InterpretAction(msg, agent_id="user_1").execute()
        guard = game.queue.get(block=False)
        guard.execute()

        out = capsys.readouterr().out
        assert "no" not in out
