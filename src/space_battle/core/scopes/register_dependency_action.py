from typing import Any, Callable

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

from .locking import scope_lock


class RegisterDependencyAction(ActionBase):
    def __init__(self, dependency: str, dependency_resolver_strategy: Callable[[list[Any]], Any]):
        self._dependency = dependency
        self._dependency_resolver_strategy = dependency_resolver_strategy

    def execute(self):
        current_scope = Ioc.resolve("IoC.Scope.Current", dict[str, Callable[[list], Any]])
        with scope_lock(current_scope):
            current_scope[self._dependency] = self._dependency_resolver_strategy
