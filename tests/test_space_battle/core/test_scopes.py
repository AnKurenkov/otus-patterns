from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction


class TestScopes:
    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self):
        InitAction().execute()
        ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()
        yield
        Ioc.resolve("IoC.Scope.Current.Clear", ActionBase).execute()

    def test_ioc_should_resolve_registered_dependency_in_current_scope(self):
        Ioc.resolve("IoC.Register", ActionBase, "someDependency", lambda *args: 1).execute()

        assert 1 == Ioc.resolve("someDependency", int)
