import logging

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.guard_action import GuardAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.game_object_base import GameObjectBase


class RecordingAction(ActionBase):
    def __init__(self, calls: list):
        self._calls = calls

    def execute(self):
        self._calls.append("executed")


@pytest.fixture()
def register_has_access():
    owners = {"ship-1": "user_1", "ship-2": "user_2"}

    def _register(mapping=None):
        effective = mapping if mapping is not None else owners
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Game.HasAccess",
            lambda agent_id, obj: effective.get(obj.id) == agent_id,
        ).execute()

    return _register


class TestGuardAction:
    def test_guard_allows_owner(self, register_has_access):
        register_has_access()
        ship = GameObjectBase("ship-1", "spaceship")
        calls = []

        GuardAction("user_1", ship, RecordingAction(calls)).execute()

        assert calls == ["executed"]

    def test_guard_denies_other_user(self, register_has_access):
        register_has_access()
        ship = GameObjectBase("ship-1", "spaceship")
        calls = []

        GuardAction("user_2", ship, RecordingAction(calls)).execute()

        assert calls == []

    def test_guard_denies_unowned_object(self, register_has_access):
        register_has_access()
        asteroid = GameObjectBase("asteroid-1", "asteroid")
        calls = []

        GuardAction("user_1", asteroid, RecordingAction(calls)).execute()

        assert calls == []

    def test_guard_logs_on_denial(self, register_has_access, caplog):
        register_has_access()
        ship = GameObjectBase("ship-1", "spaceship")

        with caplog.at_level(logging.INFO, logger="src.space_battle.core.actions.guard_action"):
            GuardAction("user_2", ship, RecordingAction([])).execute()

        assert "проигнорирована" in caplog.text
        assert "user_2" in caplog.text
