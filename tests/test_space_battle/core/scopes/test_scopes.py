import threading
from typing import Any

import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_action import InitAction


class TestScopes:
    @staticmethod
    def test_ioc_should_resolve_registered_dependency_in_current_scope():
        Ioc.resolve("IoC.Register", ActionBase, "someDependency", lambda *args: 1).execute()

        assert 1 == Ioc.resolve("someDependency", int)

    @staticmethod
    def test_ioc_should_throw_exception_on_unregistered_dependency_in_current_scope():
        with pytest.raises(Exception):
            Ioc.resolve("UnexistingDependency", int)

    @staticmethod
    def test_ioc_should_use_parent_scope_if_resolving_dependency_is_not_defined_in_current_scope():
        Ioc.resolve("IoC.Register", ActionBase, "someDependency2", lambda *args: 2).execute()

        parent_ioc_scope = Ioc.resolve("IoC.Scope.Current", Any)

        ioc_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, ioc_scope).execute()

        current_ioc_scope = Ioc.resolve("IoC.Scope.Current", Any)

        assert parent_ioc_scope != current_ioc_scope
        assert ioc_scope == current_ioc_scope
        assert 2 == Ioc.resolve("someDependency2", int)

    @staticmethod
    def test_parent_scope_can_be_set_manually_for_creating_scope():
        scope1 = Ioc.resolve("IoC.Scope.Create", Any)
        scope2 = Ioc.resolve("IoC.Scope.Create", Any, scope1)

        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope1).execute()
        Ioc.resolve("IoC.Register", ActionBase, "someDependency3", lambda *args: 3).execute()
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope2).execute()

        assert 3 == Ioc.resolve("someDependency3", int)

    @staticmethod
    def test_ioc_should_resolve_dependencies_with_same_name_in_different_threads():
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

    @staticmethod
    def test_concurrent_register_and_resolve_in_shared_scope():
        scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope).execute()

        errors = []

        def worker(worker_id: int):
            try:
                Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope).execute()
                for j in range(200):
                    dep_name = f"dep_{worker_id}_{j}"
                    Ioc.resolve("IoC.Register", ActionBase, dep_name, lambda v=worker_id: v).execute()
                    assert Ioc.resolve(dep_name, int) == worker_id
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []
        assert all(Ioc.resolve(f"dep_{i}_{j}", int) == i for i in range(4) for j in range(200))

    @staticmethod
    def test_concurrent_writes_to_same_dependency_do_not_corrupt_scope():
        scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope).execute()

        valid_values = (0, 1, 2, 3)
        errors = []

        def worker(worker_id: int):
            try:
                Ioc.resolve("IoC.Scope.Current.Set", ActionBase, scope).execute()
                for _ in range(500):
                    Ioc.resolve("IoC.Register", ActionBase, "contended", lambda v=worker_id: v).execute()
                    assert Ioc.resolve("contended", int) in valid_values
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in valid_values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []

    @staticmethod
    def test_scope_has_lock_and_scope_lock_helper():
        from src.space_battle.core.scopes.locking import scope_lock

        scope = Ioc.resolve("IoC.Scope.Create", Any)

        scope_lock_object = scope["IoC.Scope.Lock"]
        assert hasattr(scope_lock_object, "acquire") and hasattr(scope_lock_object, "release")
        assert scope_lock(scope) is scope_lock_object

        root_scope = Ioc.get_root_scope()
        root_lock = root_scope["IoC.Scope.Lock"]
        assert hasattr(root_lock, "acquire") and hasattr(root_lock, "release")
        assert scope_lock(root_scope) is root_lock

        assert scope_lock({}) is not None

    @staticmethod
    def test_get_root_scope_item():
        item = InitAction.get_root_scope_item("IoC.Register")

        assert callable(item)

    @staticmethod
    def test_init_action_execute_is_idempotent():
        InitAction().execute()
        InitAction().execute()

    @staticmethod
    def test_debug_current_info():
        info = Ioc.resolve("IoC.Scope.Debug.CurrentInfo", dict)

        assert isinstance(info, dict)
        assert "thread_name" in info
        assert "thread_id" in info
        assert "current_scope_id" in info
        assert "has_scope" in info
        assert "is_initialized" in info
