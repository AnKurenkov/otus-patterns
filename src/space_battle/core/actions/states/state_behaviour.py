from typing import Any, Optional

from src.space_battle.core.actions.base import ActionBase, ActionsLoopBase
from src.space_battle.core.ioc import Ioc

from .base import ActionsLoopStateBase


class StateActionsLoopBehaviour:
    """
    Поведение цикла обработки команд (значение свойства `ActionsLoopBase.behaviour`),
    делегирующее обработку очередной команды текущему состоянию конечного автомата
    (паттерн "Состояние").

    Подключается через уже существующий механизм `behaviour` у ActionsLoop/ServerThread —
    так же, как это делают SoftStopAction и UseSchedulerAction.

    Пример использования::

        actions_loop = ActionsLoop(queue)
        actions_loop.behaviour = StateActionsLoopBehaviour(actions_loop, NormalState())
        actions_loop.run()
    """

    def __init__(self, actions_loop: ActionsLoopBase, initial_state: ActionsLoopStateBase):
        self._actions_loop = actions_loop
        self._state: Optional[ActionsLoopStateBase] = initial_state
        # IoC-скоуп у каждого потока свой (см. ThreadScopeContext), а поведение будет
        # вызываться из потока ActionsLoop/ServerThread, а не из того потока, где оно
        # было создано. Запоминаем текущий скоуп здесь и переносим его в поток цикла
        # при первом вызове — так же, как это делает GameAction.execute().
        self._scope = Ioc.resolve("IoC.Scope.Current", Any)
        self._scope_applied = False

    def __call__(self) -> None:
        if not self._scope_applied:
            Ioc.resolve("IoC.Scope.Current.Set", ActionBase, self._scope).execute()
            self._scope_applied = True

        if self._state is None:
            self._actions_loop.stop()
            return

        self._state = self._state.handle(self._actions_loop)

        if self._state is None:
            self._actions_loop.stop()

    @property
    def state(self) -> Optional[ActionsLoopStateBase]:
        """Текущее состояние конечного автомата."""
        return self._state
