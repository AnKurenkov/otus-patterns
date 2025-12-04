from src.space_battle.core.actions.base import ActionBase

from .init_action import InitAction


class ClearCurrentScopeAction(ActionBase):

    def execute(self):
        InitAction.current_scopes.value = None
