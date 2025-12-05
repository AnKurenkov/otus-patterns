from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class DependencyResolverBase(ABC):
    @abstractmethod
    def resolve(self, dependency: str, *args: Any) -> Any: ...


class DependencyResolver(DependencyResolverBase):
    def __init__(self, scope: dict[str, Callable[[list[Any]], Any]]):
        self._dependencies = scope

    def resolve(self, dependency: str, *args: Any) -> Any:
        dependencies = self._dependencies

        while True:
            dependency_resolver_strategy: Optional[Callable[[list[Any]], Any]] = dependencies.get(dependency, None)
            if dependency_resolver_strategy:
                return dependency_resolver_strategy(*args)
            else:
                dependencies = dict[str, Callable[[list[Any]], Any]](dependencies["IoC.Scope.Parent"](*args))
