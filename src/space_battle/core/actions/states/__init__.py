from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

from .base import ActionsLoopStateBase
from .commands import HardStopCommand, MoveToCommand, RunCommand
from .move_to_state import MoveToState
from .normal_state import NormalState
from .state_behaviour import StateActionsLoopBehaviour

__all__ = [
    "ActionsLoopStateBase",
    "HardStopCommand",
    "MoveToCommand",
    "RunCommand",
    "NormalState",
    "MoveToState",
    "StateActionsLoopBehaviour",
    "register_states",
]


def register_states() -> None:
    """
    Регистрирует состояния конечного автомата обработки команд в текущем IoC-скоупе.
    Должна быть вызвана один раз при инициализации (после InitAction).
    """
    Ioc.resolve(
        "IoC.Register",
        ActionBase,
        "ActionsLoop.State.Normal",
        lambda: NormalState(),
    ).execute()

    Ioc.resolve(
        "IoC.Register",
        ActionBase,
        "ActionsLoop.State.MoveTo",
        lambda target_queue: MoveToState(target_queue),
    ).execute()
