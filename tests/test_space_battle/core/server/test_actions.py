import logging
import threading
from queue import Queue

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import SchedulerAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.actions import HardStopAction, SoftStopAction, UseSchedulerAction
from src.space_battle.core.server.server_thread import ServerThread

logger = logging.getLogger(__name__)


class TestServerThread:
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
    def test_server_thread_hard_stop(capsys, server_thread_fixture):
        q = Queue()
        server_thread = server_thread_fixture(q)
        q.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        q.put(Ioc.resolve("StubAction", ActionBase, "act2"))
        q.put(HardStopAction(server_thread))
        q.put(Ioc.resolve("StubAction", ActionBase, "act3"))

        server_thread.run()
        server_thread.wait()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" in out
        assert "act3" not in out
        assert not q.empty()

    @staticmethod
    def test_server_thread_soft_stop(capsys, server_thread_fixture):
        q = Queue()
        server_thread = server_thread_fixture(q)
        q.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        q.put(Ioc.resolve("StubAction", ActionBase, "act2"))
        q.put(SoftStopAction(server_thread))
        q.put(Ioc.resolve("StubAction", ActionBase, "act3"))

        server_thread.run()
        server_thread.wait()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" in out
        assert "act3" in out
        assert q.empty()

    @staticmethod
    def test_server_thread_use_scheduler_action(capsys, server_thread_fixture):
        q = Queue()
        server_thread = server_thread_fixture(q)
        scheduler = SchedulerAction()

        q.put(UseSchedulerAction(server_thread, scheduler))
        q.put(Ioc.resolve("StubAction", ActionBase, "act1"))
        q.put(SoftStopAction(server_thread))

        scheduler.add(Ioc.resolve("StubAction", ActionBase, "act2"))

        server_thread.run()
        server_thread.wait()

        out = capsys.readouterr().out
        assert "act1" in out
        assert "act2" in out

    @staticmethod
    def test_server_hard_stop_from_main_thread_raises(server_thread_fixture):
        server_thread = server_thread_fixture(Queue())

        with pytest.raises(Exception):
            HardStopAction(server_thread).execute()

    @staticmethod
    def test_server_soft_stop_from_main_thread_raises(server_thread_fixture):
        server_thread = server_thread_fixture(Queue())
        SoftStopAction(server_thread).execute()

        with pytest.raises(Exception):
            server_thread.behaviour()

    @staticmethod
    def test_server_use_scheduler_handles_exception(server_thread_fixture):
        server_thread = server_thread_fixture(Queue())
        scheduler = SchedulerAction()

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

        class RaisingGame:
            def execute(self):
                raise RuntimeError("boom")

        scheduler.add(RaisingGame())
        UseSchedulerAction(server_thread, scheduler).execute()

        server_thread.behaviour()

        assert len(handled) == 1

    @staticmethod
    def test_server_default_behaviour_handles_exception(server_thread_fixture):
        server_thread = server_thread_fixture(Queue())

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

        class RaisingAction(ActionBase):
            def execute(self):
                raise RuntimeError("boom")

        server_thread.queue.put(RaisingAction())

        server_thread._default_behaviour()

        assert len(handled) == 1

    @staticmethod
    def test_server_property_getters_and_setters(server_thread_fixture):
        server_thread = server_thread_fixture(Queue())

        assert callable(server_thread.before)
        assert callable(server_thread.after)

        def marker():
            pass

        server_thread.after = marker

        assert server_thread.after is marker
