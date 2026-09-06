import threading
from typing import Any, Optional

from src.space_battle.config import settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import Scope


class ApplicationScopeError(Exception):
    """Возникает, когда прикладной скоуп ещё не инициализирован."""


class InitializeApplicationScopeAction(ActionBase):
    _lock = threading.Lock()
    _initialized = False
    _application_scope: Optional[Scope] = None

    def execute(self):
        with InitializeApplicationScopeAction._lock:
            if not InitializeApplicationScopeAction._initialized:
                app_scope = Ioc.resolve("IoC.Scope.Create", Any)
                Ioc.resolve("IoC.Scope.Current.Set", ActionBase, app_scope).execute()
                Ioc.resolve("IoC.Register", ActionBase, "Config", lambda: settings).execute()
                InitializeApplicationScopeAction._application_scope = app_scope
                InitializeApplicationScopeAction._initialized = True

        Ioc.resolve(
            "IoC.Scope.Current.Set",
            ActionBase,
            InitializeApplicationScopeAction._application_scope,
        ).execute()

    @classmethod
    def get_application_scope(cls) -> Scope:
        if cls._application_scope is None:
            raise ApplicationScopeError(
                "Application scope is not initialized. " "Call InitializeApplicationScopeAction().execute() first."
            )
        return cls._application_scope
