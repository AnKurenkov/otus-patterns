from queue import Queue

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.states.commands import HardStopCommand, RunCommand
from src.space_battle.core.actions.states.move_to_state import MoveToState
from src.space_battle.core.actions.states.normal_state import NormalState
from src.space_battle.core.ioc import Ioc


class _StubActionsLoop:
    def __init__(self, queue: Queue):
        self._queue = queue

    @property
    def queue(self) -> Queue:
        return self._queue


class TestMoveToState:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        # MoveToState обращается к NormalState только через IoC, поэтому для теста
        # перехода регистрируем зависимость так же, как это делает register_states().
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "ActionsLoop.State.Normal",
            lambda: NormalState(),
        ).execute()

    @staticmethod
    def test_empty_queue_keeps_same_state():
        state = MoveToState(Queue())
        actions_loop = _StubActionsLoop(Queue())

        next_state = state.handle(actions_loop)

        assert next_state is state

    @staticmethod
    def test_regular_command_is_redirected_and_not_executed():
        executed = []

        class StubAction(ActionBase):
            def execute(self):
                executed.append(True)

        q: Queue = Queue()
        action = StubAction()
        q.put(action)
        target_queue: Queue = Queue()
        state = MoveToState(target_queue)
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert next_state is state
        assert not executed
        assert target_queue.get_nowait() is action

    @staticmethod
    def test_hard_stop_command_returns_no_next_state():
        q: Queue = Queue()
        q.put(HardStopCommand())
        state = MoveToState(Queue())
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert next_state is None

    @staticmethod
    def test_run_command_switches_to_normal_state():
        q: Queue = Queue()
        q.put(RunCommand())
        state = MoveToState(Queue())
        actions_loop = _StubActionsLoop(q)

        next_state = state.handle(actions_loop)

        assert isinstance(next_state, NormalState)
