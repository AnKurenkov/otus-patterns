from queue import Queue

from src.space_battle.core.actions.base import ActionBase, ActionsQueueBase


class HardStopCommand(ActionBase):
    """
    Команда немедленной остановки потока обработки команд.

    Сама по себе не имеет побочных эффектов — распознаётся состояниями конечного
    автомата (см. ActionsLoopStateBase.handle): её обработка приводит к возврату
    None в качестве следующего состояния, что останавливает поток.
    """

    def execute(self):
        """Маркерная команда: обрабатывается состоянием, самостоятельного действия не выполняет."""


class MoveToCommand(ActionBase):
    """
    Команда перехода в состояние MoveTo — режим, в котором последующие команды
    не выполняются, а перенаправляются в другую очередь `target_queue`.

    Обрабатывается состоянием "Обычное" (NormalState).
    """

    def __init__(self, target_queue: ActionsQueueBase | Queue):
        self._target_queue = target_queue

    @property
    def target_queue(self) -> ActionsQueueBase | Queue:
        """Очередь, в которую будут перенаправляться команды в состоянии MoveTo."""
        return self._target_queue

    def execute(self):
        """Маркерная команда: обрабатывается состоянием, самостоятельного действия не выполняет."""


class RunCommand(ActionBase):
    """
    Команда перехода в "обычное" состояние обработки команд.

    Обрабатывается состоянием MoveTo (MoveToState).
    """

    def execute(self):
        """Маркерная команда: обрабатывается состоянием, самостоятельного действия не выполняет."""
