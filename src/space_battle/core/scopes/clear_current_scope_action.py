from src.space_battle.core.actions.base import ActionBase


class ClearCurrentScopeAction(ActionBase):

    def execute(self):
        from .init_action import InitAction

        InitAction.current_scopes.value = None
