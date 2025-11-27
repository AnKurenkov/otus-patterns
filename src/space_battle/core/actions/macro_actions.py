from .actions import BurnFuel, ChangeVelocity, CheckFuel, Move, Rotate
from .base import ActionBase


class MacroAction(ActionBase):
    def __init__(self, actions: tuple):
        self._actions = actions

    def execute(self):
        for action in self._actions:
            action.execute()


class MoveWithBurnFuel(MacroAction):
    def __init__(self, actions: tuple[CheckFuel, Move, BurnFuel]):
        super().__init__(actions)


class RotateWithChangeVelocity(MacroAction):
    def __init__(self, actions: tuple[Rotate, ChangeVelocity]):
        super().__init__(actions)
