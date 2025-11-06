from collections.abc import Callable

from src.space_battle.core.actions.base import ActionBase


class ExceptionHandler:
    _store: dict[
        type, dict[type, Callable[[ActionBase, Exception], ActionBase]]
    ]  # dict[action_type, dict[exception_type, handler]]

    @staticmethod
    def handle(action: ActionBase, exception: Exception):
        action_type = type(action)
        exception_type = type(exception)
        return ExceptionHandler._store.get(action_type, {}).get(exception_type)(action, exception)

    @staticmethod
    def register(action_type: type, exception_type: type, handler: Callable[[ActionBase, Exception], ActionBase]):
        ExceptionHandler._store[action_type][exception_type] = handler
