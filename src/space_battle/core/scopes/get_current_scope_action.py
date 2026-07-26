from src.space_battle.core.actions.base import ActionBase

from .thread_scope_context import ThreadScopeContext


class GetCurrentScopeAction(ActionBase):
    def execute(self):
        return ThreadScopeContext.get_current_scope()
