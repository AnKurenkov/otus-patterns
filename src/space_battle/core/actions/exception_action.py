import logging

from src.space_battle.core.actions.base import ActionBase, ActionQueueBase

logger = logging.getLogger(__name__)


class ExceptionActionBase(ActionBase):
    """Базовый класс для действий (команд) - обработчиков исключений"""

    def __init__(self, queue: ActionQueueBase, action: ActionBase, exception: Exception):
        self._queue = queue
        self._action = action
        self._exception = exception

    def execute(self):
        pass


class LogExceptionAction(ExceptionActionBase):
    """Команда для логирования исключения"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        logger.exception(
            f"При выполнении действия (команды) {self._action} произошло исключение.", self._exception, exc_info=True
        )


class PutLogExceptionInQueueAction(ExceptionActionBase):
    """Команда, которая ставит команду, пишущую в лог в очередь команд"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        self._queue.put(LogExceptionAction(self._queue, self._action, self._exception))


class RepeatExceptionAction(ExceptionActionBase):
    """Команда для повтора команды, вызвавшей исключение"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        self._action.execute()


class SecondRepeatExceptionAction(ExceptionActionBase):
    """Команда для второго повтора команды, вызвавшей исключение"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        self._action.execute()


class PutRepeatExceptionActionInQueueAction(ExceptionActionBase):
    """Команда, которая ставит в очередь команду повторитель команды, вызвавшей исключение"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self):
        self._queue.put(RepeatExceptionAction(self._queue, self._action, self._exception))
