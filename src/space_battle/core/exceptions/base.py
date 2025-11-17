from abc import ABC, abstractmethod
from typing import Type, TypeVar

from src.space_battle.core.actions.base import ActionBase, ActionQueueBase
from src.space_battle.core.actions.exception_action import ExceptionActionBase


class SpaceBattleError(Exception):
    """Базовый класс для всех исключений в проекте."""


AT = TypeVar("AT", bound=ActionBase)
ET = TypeVar("ET", bound=SpaceBattleError)
HT = TypeVar("HT", bound=ExceptionActionBase)


class ExceptionHandlerBase(ABC):
    """Абстрактный базовый класс обработчика исключений.
    Обязательный атрибут:
    _store : dict[тип действия, dict[тип исключения, тип обработчика]]
    """

    _store: dict[Type[AT], dict[Type[ET], Type[HT]]] = {}

    @staticmethod
    @abstractmethod
    def handle(queue: ActionQueueBase, action: ActionBase, exception: Exception) -> ExceptionActionBase:
        """Обработать исключение"""

    @staticmethod
    @abstractmethod
    def register(action_type: Type[AT], exception_type: Type[ET], handler_type: Type[HT]):
        """Зарегистрировать обработчик для пары действие/исключение"""
