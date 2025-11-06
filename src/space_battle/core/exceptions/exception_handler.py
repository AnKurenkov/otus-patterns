from src.space_battle.core.actions.base import ActionBase, ActionQueueBase
from src.space_battle.core.actions.exception_action import ExceptionActionBase, LogExceptionAction


class ExceptionHandler:
    _store: dict[type, dict[type, ExceptionActionBase]]  # dict[action_type, dict[exception_type, handler]]

    @staticmethod
    def handle(queue: ActionQueueBase, action: ActionBase, exception: Exception) -> ExceptionActionBase:
        action_type = type(action)
        exception_type = type(exception)
        return ExceptionHandler._store.get(action_type, {}).get(exception_type, LogExceptionAction)(
            queue, action, exception
        )

    @staticmethod
    def register(action_type: type, exception_type: type, handler: ExceptionActionBase):
        ExceptionHandler._store[action_type][exception_type] = handler
