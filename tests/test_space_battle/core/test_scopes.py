import threading
from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction


class TestScopes:
    @pytest.fixture(scope="function", autouse=True)
    def test_setup(self):
        InitAction().execute()
        ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()
        yield
        Ioc.resolve("IoC.Scope.Current.Clear", ActionBase).execute()

    def test_ioc_should_resolve_registered_dependency_in_current_scope(self):
        Ioc.resolve("IoC.Register", ActionBase, "someDependency", lambda *args: 1).execute()

        assert 1 == Ioc.resolve("someDependency", int)

    def test_ioc_should_throw_exception_on_unregistered_dependency_in_current_scope(self):
        with pytest.raises(Exception):
            Ioc.resolve("UnexistingDependency", int)

    def test_ioc_should_use_parent_scope_if_resolving_dependency_is_not_defined_in_current_scope(self):
        Ioc.resolve("IoC.Register", ActionBase, "someDependency2", lambda *args: 2).execute()

        parent_ioc_scope = Ioc.resolve("IoC.Scope.Current", Any)

        ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()

        current_ioc_scope = Ioc.resolve("IoC.Scope.Current", Any)

        assert parent_ioc_scope != current_ioc_scope
        assert ioc_scope == current_ioc_scope
        assert 2 == Ioc.resolve("someDependency2", int)

    def test_parent_scope_can_be_set_manually_for_creating_scope(self):
        scope1 = Ioc.resolve("IoC.Scope.Create", Any)
        scope2 = Ioc.resolve("IoC.Scope.Create", Any, scope1)

        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope1).execute()
        Ioc.resolve("IoC.Register", ActionBase, "someDependency3", lambda *args: 3).execute()
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope2).execute()

        assert 3 == Ioc.resolve("someDependency3", int)

    def test_ioc_should_resolve_dependencies_with_same_name_in_different_threads(self):
        scope1 = Ioc.resolve("IoC.Scope.Create", Any)
        scope2 = Ioc.resolve("IoC.Scope.Create", Any)

        def worker(scope, ret_val: int):
            Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope).execute()
            Ioc.resolve("IoC.Register", ActionBase, "sameDependency", lambda *args: ret_val).execute()
            assert ret_val == Ioc.resolve("sameDependency", int)

        thread1 = threading.Thread(target=worker, args=(scope1, 1))
        thread2 = threading.Thread(target=worker, args=(scope2, 2))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
