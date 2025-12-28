from typing import Type

from src.space_battle.core.actions.base import ActionBase, ActionsQueueBase
from src.space_battle.core.actions.exception_action import ExceptionActionBase, LogExceptionAction

from .base import AT, ET, HT, ExceptionHandlerBase


class ExceptionHandler(ExceptionHandlerBase):
    default_exception_action: ExceptionActionBase = LogExceptionAction

    @staticmethod
    def handle(queue: ActionsQueueBase, action: ActionBase, exception: Exception) -> ExceptionActionBase:
        action_type = type(action)
        exception_type = type(exception)
        return ExceptionHandler._store.get(action_type, {}).get(
            exception_type, ExceptionHandler.default_exception_action
        )(queue, action, exception)

    @staticmethod
    def register(action_type: Type[AT], exception_type: Type[ET], handler_type: Type[HT]):
        ExceptionHandler._store[action_type] = {}
        ExceptionHandler._store[action_type][exception_type] = handler_type
