from queue import Queue

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.states.commands import HardStopCommand, MoveToCommand
from src.space_battle.core.actions.states.move_to_state import MoveToState
from src.space_battle.core.actions.states.normal_state import NormalState
from src.space_battle.core.ioc import Ioc


class _StubActionsLoop:
    """Минимальная заглушка ActionsLoopBase для изолированного тестирования состояний."""

    def __init__(self, queue: Queue):
        self._queue = queue

    @property
    def queue(self) -> Queue:
        return self._queue


class TestNormalState:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        # NormalState обращается к MoveToState только через IoC, поэтому для теста
        # перехода регистрируем зависимость так же, как это делает register_states().
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "ActionsLoop.State.MoveTo",
            lambda target_queue: MoveToState(target_queue),
        ).execute()

    @staticmethod
    def test_empty_queue_keeps_same_state():
        state = NormalState()
        actions_loop = _StubActionsLoop(Queue())

        next_state = state.handle(actions_loop)

        assert next_state is state

    @staticmethod
    def test_regular_command_is_executed_and_state_is_kept(capsys):
        class StubAction(ActionBase):
            def execute(self):
                print("executed")

        q: Queue = Queue()
        q.put(StubAction())
        state = NormalState()
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert next_state is state
        assert "executed" in capsys.readouterr().out

    @staticmethod
    def test_hard_stop_command_returns_no_next_state():
        q: Queue = Queue()
        q.put(HardStopCommand())
        state = NormalState()
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert next_state is None

    @staticmethod
    def test_move_to_command_switches_to_move_to_state():
        q: Queue = Queue()
        target_queue: Queue = Queue()
        q.put(MoveToCommand(target_queue))
        state = NormalState()
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert isinstance(next_state, MoveToState)
