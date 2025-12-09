from src.space_battle.core.actions.base import ActionBase


class SetCurrentScopeAction(ActionBase):
    def __init__(self, scope):
        self._scope = scope

    def execute(self):
        from .init_action import InitAction

        InitAction.current_scopes.value = self._scope
