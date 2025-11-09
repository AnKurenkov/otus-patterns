from typing import Type

from src.space_battle.core.actions.exception_action import (
    LogExceptionAction,
    PutRepeatExceptionActionInQueueAction,
    RepeatExceptionAction,
)

from .base import AT, ET
from .exception_handler import ExceptionHandler


class RepeatThenLogExceptionHandlerStrategy:
    @staticmethod
    def set(action_type: Type[AT], exception_type: Type[ET]):
        ExceptionHandler.register(action_type, exception_type, PutRepeatExceptionActionInQueueAction)
        ExceptionHandler.register(RepeatExceptionAction, exception_type, LogExceptionAction)
