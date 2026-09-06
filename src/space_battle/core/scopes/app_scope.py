from typing import Any, Optional

from src.space_battle.config import settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import Scope


class ApplicationScopeError(Exception):
    """Возникает, когда прикладной скоуп ещё не инициализирован."""


_APPLICATION_SCOPE: Optional[Scope] = None


def initialize_application_scope() -> Scope:
    """
    Создаёт прикладной скоуп (родитель — текущий скоуп на момент вызова,
    обычно корневой) и регистрирует в нём зависимость "Config", указывающую
    на модульный синглтон settings из config.py.

    Скоуп становится текущим в вызывающем потоке, поэтому все созданные далее
    игровые скоупы получают его родителем и могут резолвить "Config" через
    цепочку IoC.Scope.Parent.

    Повторный вызов (например, из другого потока) лишь делает сохранённый
    прикладной скоуп текущим в этом потоке.
    """
    global _APPLICATION_SCOPE

    if _APPLICATION_SCOPE is None:
        app_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, app_scope).execute()
        Ioc.resolve("IoC.Register", ActionBase, "Config", lambda: settings).execute()
        _APPLICATION_SCOPE = app_scope

    Ioc.resolve("IoC.Scope.Current.Set", ActionBase, _APPLICATION_SCOPE).execute()
    return _APPLICATION_SCOPE


def get_application_scope() -> Scope:
    """Возвращает прикладной скоуп, выбрасывая ошибку, если он не создан."""
    if _APPLICATION_SCOPE is None:
        raise ApplicationScopeError("Application scope is not initialized. Call initialize_application_scope() first.")
    return _APPLICATION_SCOPE
