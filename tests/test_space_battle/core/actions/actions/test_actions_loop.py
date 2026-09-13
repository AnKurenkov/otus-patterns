import logging
import threading
from queue import Queue

import pytest

from src.space_battle.core.actions.actions_loop import ActionsLoop
from src.space_battle.core.actions.actions_loop_actions import HardStopAction, SoftStopAction
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

logger = logging.getLogger(__name__)


class TestActionsLoop:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        class StubAction(ActionBase):
            def __init__(self, msg):
                self._msg = msg

            def execute(self):
                print(self._msg)

        class StubEventAction(ActionBase):
            def __init__(self, event: threading.Event):
                self._event = event

            def execute(self):
                self._event.set()

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubAction",
            lambda msg: StubAction(msg),
        ).execute()

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubEventAction",
            lambda event: StubEventAction(event),
        ).execute()

    @staticmethod
    @pytest.fixture()
    def actions_loop_fixture():
        actions_loop: ActionsLoop | None = None

        def _create(queue):
            nonlocal actions_loop
            actions_loop = ActionsLoop(queue)
            return actions_loop

        yield _create

        if actions_loop:
            actions_loop.stop()

    @staticmethod
    def test_actions_loop_start(actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)
        event = threading.Event()
        actions_loop.before = event.set
        actions_loop.run()
        assert event.wait(timeout=1)

    @staticmethod
    def test_before_after_property_getters(actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)
        assert callable(actions_loop.before)
        assert callable(actions_loop.after)

    @staticmethod
    def test_default_behaviour_handles_exception(actions_loop_fixture):
        class RaisesAction(ActionBase):
            def execute(self):
                raise RuntimeError("boom")

        handled = []

        class HandleExceptionStub(ActionBase):
            def __init__(self, action, exception):
                self._action = action
                self._exception = exception
                handled.append((self._action, self._exception))

            def execute(self):
                pass

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "HandleException",
            lambda action, exception: HandleExceptionStub(action, exception),
        ).execute()

        q = Queue()
        actions_loop = ActionsLoop(q)
        q.put(RaisesAction())

        actions_loop._default_behaviour()

        assert len(handled) == 1
        assert isinstance(handled[0][0], RaisesAction)

    @staticmethod
    def test_hard_stop_from_main_thread_raises(actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)

        with pytest.raises(Exception):
            HardStopAction(actions_loop).execute()

    @staticmethod
    def test_soft_stop_from_main_thread_raises(actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)
        SoftStopAction(actions_loop).execute()

        with pytest.raises(Exception):
            actions_loop.behaviour()

    @staticmethod
    def test_actions_loop_hard_stop(capsys, actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)
        q.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        q.put(Ioc.resolve("StubAction", ActionBase, "act2"))
        q.put(HardStopAction(actions_loop))
        q.put(Ioc.resolve("StubAction", ActionBase, "act3"))

        event = threading.Event()
        actions_loop.after = event.set

        actions_loop.run()

        # assert event.wait(timeout=1)
        actions_loop.wait()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" in out
        assert "act3" not in out
        assert not q.empty()

    @staticmethod
    def test_actions_loop_soft_stop(capsys, actions_loop_fixture):
        q = Queue()
        actions_loop = actions_loop_fixture(q)
        q.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        q.put(Ioc.resolve("StubAction", ActionBase, "act2"))
        q.put(SoftStopAction(actions_loop))
        q.put(Ioc.resolve("StubAction", ActionBase, "act3"))

        event = threading.Event()
        actions_loop.after = event.set

        actions_loop.run()

        # assert event.wait(timeout=1)
        actions_loop.wait()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" in out
        assert "act3" in out
        assert q.empty()
