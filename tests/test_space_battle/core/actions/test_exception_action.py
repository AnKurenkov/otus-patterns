from unittest.mock import Mock

import pytest

from src.space_battle.core.actions.base import ActionBase, ActionsQueueBase
from src.space_battle.core.actions.exception_actions import (
    LogExceptionAction,
    PutLogExceptionInQueueAction,
    PutRepeatExceptionInQueueAction,
)
from src.space_battle.core.exceptions.base import SpaceBattleError


@pytest.fixture
def mock_queue():
    return Mock(spec=ActionsQueueBase)


@pytest.fixture
def mock_action():
    return Mock(spec=ActionBase)


@pytest.fixture
def stub_exception():
    return SpaceBattleError("Тест")


class TestExceptionAction:
    @staticmethod
    def test_log_exception_action(caplog, mock_queue, mock_action, stub_exception):
        LogExceptionAction(mock_queue, mock_action, stub_exception).execute()
        assert caplog.records[0].levelname == "ERROR"
        assert f"При выполнении действия (команды) {type(mock_action)} произошло исключение" in caplog.text

    @staticmethod
    def test_put_log_exception_in_queue_action(mock_queue, mock_action, stub_exception):
        PutLogExceptionInQueueAction(mock_queue, mock_action, stub_exception).execute()
        mock_queue.put.assert_called_once()

    @staticmethod
    def test_put_repeat_exception_in_queue_action(mock_queue, mock_action, stub_exception):
        PutRepeatExceptionInQueueAction(mock_queue, mock_action, stub_exception).execute()
        mock_queue.put.assert_called_once()
