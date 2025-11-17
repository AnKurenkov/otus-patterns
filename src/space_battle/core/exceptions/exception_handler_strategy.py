from typing import Type

from src.space_battle.core.actions.exception_action import (
    LogExceptionAction,
    PutRepeatExceptionInQueueAction,
    PutSecondRepeatExceptionInQueueAction,
    RepeatExceptionAction,
    SecondRepeatExceptionAction,
)

from .base import AT, ET
from .exception_handler import ExceptionHandler


class RepeatThenLogExceptionHandlerStrategy:
    @staticmethod
    def set(action_type: Type[AT], exception_type: Type[ET]):
        ExceptionHandler.register(action_type, exception_type, PutRepeatExceptionInQueueAction)
        ExceptionHandler.register(RepeatExceptionAction, exception_type, LogExceptionAction)


class RepeatTwiceThenLogExceptionHandlerStrategy:
    @staticmethod
    def set(action_type: Type[AT], exception_type: Type[ET]):
        ExceptionHandler.register(action_type, exception_type, PutRepeatExceptionInQueueAction)
        ExceptionHandler.register(RepeatExceptionAction, exception_type, PutSecondRepeatExceptionInQueueAction)
        ExceptionHandler.register(SecondRepeatExceptionAction, exception_type, LogExceptionAction)
