from src.space_battle.core.actions.base import ActionBase

from .init_action import InitAction


class SetCurrentScopeAction(ActionBase):
    def __init__(self, scope):
        self._scope = scope

    def execute(self):
        InitAction.current_scopes.value = self._scope
