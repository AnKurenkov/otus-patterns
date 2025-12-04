import threading
from typing import Any, Callable, Dict

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

from .clear_current_scope_action import ClearCurrentScopeAction
from .dependency_resolver import DependencyResolver
from .register_dependency_action import RegisterDependencyAction
from .set_current_scope_action import SetCurrentScopeAction


class InitAction(ActionBase):
    current_scopes = threading.local()
    _root_scope_lock = threading.Lock()
    _root_scope: Dict[str, Callable[[list], Any]] = {}
    _already_executes_successfully = False

    @staticmethod
    def _raise_exception(note):
        raise Exception(note)

    @staticmethod
    def _creating_scope(*args):
        creating_scope = Ioc.resolve("IoC.Scope.Create.Empty", Dict[str, Callable[[list], Any]])
        if len(args) > 0:
            parent_scope = args[0]
        else:
            parent_scope = Ioc.resolve("IoC.Scope.Current", Any)
        creating_scope["IoC.Scope.Parent"] = lambda *args_: parent_scope
        return creating_scope

    @staticmethod
    def _dependency_resolver_resolve(dependency: str, *args):
        scope = (
            InitAction.current_scopes.value if InitAction.current_scopes.value is not None else InitAction.root_scope
        )
        dependency_resolver = DependencyResolver(scope)
        return dependency_resolver.resolve(dependency, args)

    @property
    def root_scope(self) -> Dict[str, Callable[[list], Any]]:
        return self._root_scope

    @classmethod
    def get_root_scope_item(cls, key: str) -> Callable[[list], Any]:
        with cls._root_scope_lock:
            return cls._root_scope.get(key)

    @classmethod
    def set_root_scope_item(cls, key: str, scope: Callable[[list], Any]):
        with cls._root_scope_lock:
            cls._root_scope[key] = scope

    def execute(self):
        if self._already_executes_successfully:
            return

        InitAction.set_root_scope_item("IoC.Scope.Current.Set", lambda *args: SetCurrentScopeAction(args[0]))

        InitAction.set_root_scope_item("IoC.Scope.Current.Clear", lambda *args: ClearCurrentScopeAction())

        InitAction.set_root_scope_item(
            "IoC.Scope.Current",
            lambda *args: self.current_scopes.value if self.current_scopes.value is not None else self.root_scope,
        )

        InitAction.set_root_scope_item(
            "IoC.Scope.Current.Parent",
            lambda *args: InitAction._raise_exception("The root scope has no a parent scope."),
        )

        InitAction.set_root_scope_item("IoC.Scope.Current.Empty", lambda *args: Dict[str, Callable[[list], Any]]())

        InitAction.set_root_scope_item("IoC.Scope.Current.Create", lambda *args: InitAction._creating_scope(args))

        InitAction.set_root_scope_item(
            "IoC.Register", lambda *args: RegisterDependencyAction(str(args[0]), Callable[[list[Any]], Any](args[1]))
        )

        Ioc.resolve(
            "Update Ioc Resolve Dependency Strategy",
            ActionBase,
            lambda old_strategy: lambda dependency, *args: InitAction._dependency_resolver_resolve(dependency, args),
        ).execute()

        self._already_executes_successfully = True
