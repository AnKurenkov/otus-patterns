from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from .locking import scope_lock


class DependencyResolverBase(ABC):
    @abstractmethod
    def resolve(self, dependency: str, *args: Any) -> Any: ...


class DependencyResolver(DependencyResolverBase):
    def __init__(self, scope: dict[str, Callable[[list[Any]], Any]]):
        self._dependencies = scope

    def resolve(self, dependency: str, *args: Any) -> Any:
        dependencies = self._dependencies

        while True:
            with scope_lock(dependencies):
                dependency_resolver_strategy: Optional[Callable[[list[Any]], Any]] = dependencies.get(dependency, None)
                parent_resolver_strategy = None
                if dependency_resolver_strategy is None:
                    parent_resolver_strategy = dependencies["IoC.Scope.Parent"]

            if dependency_resolver_strategy is not None:
                return dependency_resolver_strategy(*args)
            else:
                dependencies = dict[str, Callable[[list[Any]], Any]](parent_resolver_strategy(*args))
