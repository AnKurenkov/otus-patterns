from src.space_battle.core.actions.base import ActionBase

from .thread_scope_context import ThreadScopeContext


class SetCurrentScopeAction(ActionBase):
    def __init__(self, scope):
        self._scope = scope

    def execute(self):
        ThreadScopeContext.set_current_scope(self._scope)
