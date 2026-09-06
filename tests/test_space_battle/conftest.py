import logging
from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def ioc_scopes_init_action():
    InitAction().execute()
    InitializeApplicationScopeAction().execute()


@pytest.fixture(scope="module", autouse=True)
def ioc_scope_create():
    app_scope = InitializeApplicationScopeAction.get_application_scope()
    ioc_scope = Ioc.resolve("IoC.Scope.Create", Any, app_scope)
    Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()
    yield
    Ioc.resolve("IoC.Scope.Current.Clear", ActionBase).execute()
