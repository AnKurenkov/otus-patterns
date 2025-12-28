import queue
from unittest.mock import Mock

import pytest

from src.space_battle.core.actions.base import ActionBase, ActionsQueueBase
from src.space_battle.core.actions.exception_action import (
    LogExceptionAction,
    PutRepeatExceptionInQueueAction,
    PutSecondRepeatExceptionInQueueAction,
    RepeatExceptionAction,
    SecondRepeatExceptionAction,
)
from src.space_battle.core.exceptions.base import SpaceBattleError
from src.space_battle.core.exceptions.exception_handler import ExceptionHandler
from src.space_battle.core.exceptions.exception_handler_strategy import (
    RepeatThenLogExceptionHandlerStrategy,
    RepeatTwiceThenLogExceptionHandlerStrategy,
)


@pytest.fixture
def mock_action():
    return Mock(spec=ActionBase)


@pytest.fixture
def stub_queue():
    class StubActionsQueue(ActionsQueueBase):
        _queue = queue.Queue()

        def put(self, action: ActionBase, *args, **kwargs):
            self._queue.put(action)
            return True

        def get(self) -> ActionBase:
            return self._queue.get()

    return StubActionsQueue()


@pytest.fixture
def stub_exception():
    return SpaceBattleError("Тестовая ошибка.")


class TestExceptionHandlerStrategy:
    @staticmethod
    def test_repeat_then_log_exception_handler_strategy(caplog, stub_queue, mock_action, stub_exception):
        # 0. Задаём стратегию обработки исключений
        RepeatThenLogExceptionHandlerStrategy.set(type(mock_action), type(stub_exception))
        assert ExceptionHandler._store[type(mock_action)][type(stub_exception)] == PutRepeatExceptionInQueueAction
        assert ExceptionHandler._store[RepeatExceptionAction][type(stub_exception)] == LogExceptionAction
        # 1. Виртуально выполнили действие mock_action, получили исключение stub_exception для обработки
        exception_action = ExceptionHandler.handle(stub_queue, mock_action, stub_exception)
        assert type(exception_action) is PutRepeatExceptionInQueueAction
        # 2. Выполняем обработчик PutRepeatExceptionInQueueAction - в очередь попадает RepeatExceptionAction
        exception_action.execute()
        repeat_action = stub_queue.get()
        assert type(repeat_action) is RepeatExceptionAction
        # 3. Выполняем действие RepeatExceptionAction, повторно выполняется mock_action,
        # получили исключение stub_exception для обработки
        repeat_action.execute()
        mock_action.execute.assert_called_once()
        exception_action = ExceptionHandler.handle(stub_queue, repeat_action, stub_exception)
        assert type(exception_action) is LogExceptionAction
        # 4. Выполняем обработчик LogExceptionAction
        exception_action.execute()
        assert "произошло исключение: SpaceBattleError: Тестовая ошибка" in caplog.text

    @staticmethod
    def test_repeat_twice_then_log_exception_handler_strategy(caplog, stub_queue, mock_action, stub_exception):
        # 0. Задаём стратегию обработки исключений
        RepeatTwiceThenLogExceptionHandlerStrategy.set(type(mock_action), type(stub_exception))
        assert ExceptionHandler._store[type(mock_action)][type(stub_exception)] == PutRepeatExceptionInQueueAction
        assert (
            ExceptionHandler._store[RepeatExceptionAction][type(stub_exception)]
            == PutSecondRepeatExceptionInQueueAction
        )
        assert ExceptionHandler._store[SecondRepeatExceptionAction][type(stub_exception)] == LogExceptionAction
        # 1. Виртуально выполнили действие mock_action, получили исключение stub_exception для обработки
        exception_action = ExceptionHandler.handle(stub_queue, mock_action, stub_exception)
        assert type(exception_action) is PutRepeatExceptionInQueueAction
        # 2. Выполняем обработчик PutRepeatExceptionInQueueAction - в очередь попадает RepeatExceptionAction
        exception_action.execute()
        repeat_action = stub_queue.get()
        assert type(repeat_action) is RepeatExceptionAction
        # 3. Выполняем действие RepeatExceptionAction, повторно выполняется mock_action,
        # получили исключение stub_exception для обработки
        repeat_action.execute()
        mock_action.execute.assert_called_once()
        exception_action = ExceptionHandler.handle(stub_queue, repeat_action, stub_exception)
        assert type(exception_action) is PutSecondRepeatExceptionInQueueAction
        # 4. Выполняем обработчик PutSecondRepeatExceptionInQueueAction - в очередь попадает SecondRepeatExceptionAction
        exception_action.execute()
        repeat_action = stub_queue.get()
        assert type(repeat_action) is SecondRepeatExceptionAction
        # 5. Выполняем действие SecondRepeatExceptionAction, повторно выполняется mock_action,
        # получили исключение stub_exception для обработки
        repeat_action.execute()
        assert mock_action.execute.call_count == 2
        exception_action = ExceptionHandler.handle(stub_queue, repeat_action, stub_exception)
        assert type(exception_action) is LogExceptionAction
        # 6. Выполняем обработчик LogExceptionAction
        exception_action.execute()
        assert "произошло исключение: SpaceBattleError: Тестовая ошибка" in caplog.text
