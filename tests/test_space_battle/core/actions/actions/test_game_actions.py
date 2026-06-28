import logging
from queue import Queue
from time import sleep

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import GameAction, GameInitAction, GameStopAction, SchedulerAction
from src.space_battle.core.ioc import Ioc

logger = logging.getLogger(__name__)


class TestGameActions:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        class StubAction(ActionBase):
            def __init__(self, msg):
                self._msg = msg

            def execute(self):
                print(self._msg)

        class StubSleepAction(ActionBase):
            def __init__(self, time_sec: float):
                self._time_sec = time_sec

            def execute(self):
                sleep(self._time_sec)

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubAction",
            lambda msg: StubAction(msg),
        ).execute()

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubSleepAction",
            lambda time_sec: StubSleepAction(time_sec),
        ).execute()

    @staticmethod
    def test_game_action(capsys):
        Ioc.resolve("IoC.Register", ActionBase, "Game.Init", lambda init: GameInitAction(init)).execute()
        scheduler = SchedulerAction()
        game_action = GameAction(0.05, scheduler)
        game_queue = Ioc.resolve("Game.Queue", Queue)

        game_queue.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        game_queue.put(GameStopAction())
        game_queue.put(Ioc.resolve("StubAction", ActionBase, "act2"))

        game_action.execute()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" not in out

    @staticmethod
    def test_scheduler_action(capsys):
        Ioc.resolve("IoC.Register", ActionBase, "Game.Init", lambda init: GameInitAction(init)).execute()
        scheduler = SchedulerAction()
        game_action = GameAction(0.05, scheduler)  # TODO: определить init и передать в игру
        game_queue = Ioc.resolve("Game.Queue", Queue)

        game_queue.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        game_queue.put(Ioc.resolve("StubSleepAction", ActionBase, 0.1))
        game_queue.put(Ioc.resolve("StubAction", ActionBase, "act2"))
        game_queue.put(GameStopAction())

        game_action.execute()
        out = capsys.readouterr().out
        assert "act1" in out

        scheduler.execute()
        out = capsys.readouterr().out
        assert "act2" in out
