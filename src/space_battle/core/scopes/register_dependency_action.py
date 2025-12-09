from typing import Any, Callable

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc


class RegisterDependencyAction(ActionBase):
    def __init__(self, dependency: str, dependency_resolver_strategy: Callable[[list[Any]], Any]):
        self._dependency = dependency
        self._dependency_resolver_strategy = dependency_resolver_strategy

    def execute(self):
        current_scope = Ioc.resolve("IoC.Scope.Current", dict[str, Callable[[list], Any]])
        current_scope[self._dependency] = self._dependency_resolver_strategy
