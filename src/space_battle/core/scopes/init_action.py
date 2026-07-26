import threading
from typing import Any, Callable, Optional, TypeAlias, cast

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

from .clear_current_scope_action import ClearCurrentScopeAction
from .dependency_resolver import DependencyResolver
from .register_dependency_action import RegisterDependencyAction
from .set_current_scope_action import SetCurrentScopeAction
from .thread_scope_context import ThreadScopeContext

Scope: TypeAlias = dict[str, Callable[[list], Any]]


class InitAction(ActionBase):
    _lock = threading.Lock()
    _initialized = False
    _root_scope: Optional[Scope] = None

    @staticmethod
    def _raise_exception(note):
        raise Exception(note)

    @staticmethod
    def _dependency_resolver_resolve(dependency: str, *args):
        dependency_resolver = DependencyResolver(InitAction._get_current_scope())
        return dependency_resolver.resolve(dependency, *args)

    @staticmethod
    def _create_scope(*args):
        created_scope = Ioc.resolve("IoC.Scope.Create.Empty", dict)
        if args:
            parent_scope = args[0]
        else:
            parent_scope = Ioc.resolve("IoC.Scope.Current", Any)
        created_scope["IoC.Scope.Parent"] = lambda *args_: parent_scope
        return created_scope

    @classmethod
    def _get_root_scope(cls) -> Scope:
        if cls._root_scope is None:
            cls._root_scope = Ioc.get_root_scope()
        return cls._root_scope

    @classmethod
    def _get_current_scope(cls) -> Scope:
        current = ThreadScopeContext.get_current_scope()
        return current if current is not None else cls._get_root_scope()

    @classmethod
    def get_root_scope_item(cls, key: str) -> Callable[[list], Any]:
        with cls._lock:
            return cls._get_root_scope().get(key)

    @classmethod
    def set_root_scope_item(cls, key: str, scope: Callable[[list], Any]):
        with cls._lock:
            cls._get_root_scope()[key] = scope

    def execute(self):
        if InitAction._initialized:
            return

        InitAction.set_root_scope_item("IoC.Scope.Current.Set", lambda *args: SetCurrentScopeAction(args[0]))

        InitAction.set_root_scope_item("IoC.Scope.Current.Clear", lambda *args: ClearCurrentScopeAction())

        InitAction.set_root_scope_item(
            "IoC.Scope.Current",
            lambda *args: InitAction._get_current_scope(),
        )

        InitAction.set_root_scope_item(
            "IoC.Scope.Parent",
            lambda *args: self._raise_exception("The root scope has no a parent scope."),
        )

        InitAction.set_root_scope_item("IoC.Scope.Create.Empty", lambda *args: dict())

        InitAction.set_root_scope_item("IoC.Scope.Create", lambda *args: self._create_scope(*args))

        InitAction.set_root_scope_item(
            "IoC.Register",
            lambda *args: RegisterDependencyAction(str(args[0]), cast(Callable[[list[Any]], Any], args[1])),
        )

        InitAction.set_root_scope_item("IoC.Scope.Debug.CurrentInfo", lambda: InitAction._debug_current_info())

        Ioc.resolve(
            "Update Ioc Resolve Dependency Strategy",
            ActionBase,
            lambda old_strategy: lambda dependency, *args: InitAction._dependency_resolver_resolve(dependency, *args),
        ).execute()

        InitAction._initialized = True

    @staticmethod
    def _debug_current_info():
        """Отладочная информация о текущем потоке и скоупе"""
        current = ThreadScopeContext.get_current_scope()
        return {
            "thread_name": threading.current_thread().name,
            "thread_id": threading.current_thread().ident,
            "current_scope_id": id(current) if current else None,
            "has_scope": current is not None,
            "is_initialized": InitAction._initialized,
        }
