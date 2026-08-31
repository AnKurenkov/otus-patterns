import logging
import threading
import time
from queue import Queue

import pytest

from src.space_battle.core.actions.actions_loop import ActionsLoop
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.states import (
    HardStopCommand,
    MoveToCommand,
    MoveToState,
    NormalState,
    RunCommand,
    StateActionsLoopBehaviour,
    register_states,
)
from src.space_battle.core.ioc import Ioc

logger = logging.getLogger(__name__)


class TestStateActionsLoopBehaviour:
    """
    Проверяет, что поток обработки команд (ActionsLoop), подключивший конечный автомат
    состояний через StateActionsLoopBehaviour, действительно переключает режим обработки
    команд начиная со следующей команды.
    """

    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def class_setup():
        register_states()

        class StubAction(ActionBase):
            def __init__(self, msg):
                self._msg = msg

            def execute(self):
                print(self._msg)

        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "StubAction",
            lambda msg: StubAction(msg),
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
    def test_move_to_command_switches_thread_to_move_to_state(actions_loop_fixture):
        q: Queue = Queue()
        target_queue: Queue = Queue()
        actions_loop = actions_loop_fixture(q)
        behaviour = StateActionsLoopBehaviour(actions_loop, NormalState())
        actions_loop.behaviour = behaviour

        # Команда, выполненная до перехода, - обычным образом.
        q.put(Ioc.resolve("StubAction", ActionBase, "before-move-to"))
        # Команда перехода в состояние MoveTo.
        q.put(MoveToCommand(target_queue))

        actions_loop.run()

        # Ждём (с таймаутом), пока поток обработает команду перехода.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not isinstance(behaviour.state, MoveToState):
            time.sleep(0.01)

        assert isinstance(behaviour.state, MoveToState), "Поток должен перейти в состояние MoveTo"

        # Команда, отправленная после перехода, должна не выполняться, а перенаправляться.
        q.put(Ioc.resolve("StubAction", ActionBase, "after-move-to-should-be-redirected"))
        redirected_action = target_queue.get(timeout=1)
        assert redirected_action is not None

        actions_loop.stop()
        actions_loop.wait()

    @staticmethod
    def test_run_command_switches_thread_back_to_normal_state(actions_loop_fixture):
        q: Queue = Queue()
        target_queue: Queue = Queue()
        actions_loop = actions_loop_fixture(q)
        # Стартуем сразу в состоянии MoveTo.
        behaviour = StateActionsLoopBehaviour(actions_loop, MoveToState(target_queue))
        actions_loop.behaviour = behaviour

        q.put(RunCommand())

        actions_loop.run()

        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not isinstance(behaviour.state, NormalState):
            time.sleep(0.01)

        assert isinstance(behaviour.state, NormalState), "Поток должен вернуться в 'обычное' состояние"

        # После возврата в обычное состояние команды снова выполняются, а не перенаправляются.
        q.put(Ioc.resolve("StubAction", ActionBase, "after-run-should-be-executed"))
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline and not q.empty():
            time.sleep(0.01)
        assert target_queue.empty()

        actions_loop.stop()
        actions_loop.wait()

    @staticmethod
    def test_hard_stop_command_terminates_thread(actions_loop_fixture, capsys):
        q: Queue = Queue()
        actions_loop = actions_loop_fixture(q)
        behaviour = StateActionsLoopBehaviour(actions_loop, NormalState())
        actions_loop.behaviour = behaviour

        # Команды до HardStop выполняются, после — нет.
        q.put(Ioc.resolve("StubAction", ActionBase, "before-hard-stop"))
        q.put(HardStopCommand())
        q.put(Ioc.resolve("StubAction", ActionBase, "after-hard-stop"))

        # Сигнал о выходе из цикла (вызов _after), если поток завершился сам.
        terminated = threading.Event()
        actions_loop.after = terminated.set

        actions_loop.run()

        # Поток должен завершиться по HardStopCommand, а не по команде stop() извне.
        assert terminated.wait(timeout=2), "Поток не завершился после HardStopCommand"

        actions_loop.wait()

        out = capsys.readouterr().out
        assert "before-hard-stop" in out
        assert "after-hard-stop" not in out
        assert not q.empty()
