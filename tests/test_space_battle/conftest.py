from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction


@pytest.fixture(scope="session", autouse=True)
def ioc_scopes_init_action():
    InitAction().execute()


@pytest.fixture(autouse=True)
def ioc_scope_create():
    ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
    Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()
    yield
    Ioc.resolve("IoC.Scope.Current.Clear", ActionBase).execute()
