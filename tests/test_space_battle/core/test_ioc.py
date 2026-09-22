import pytest

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc


class TestIoc:
    @staticmethod
    @pytest.mark.skip(reason="Доработать, т.к. выполнение InitAction() ломает тест")
    def test_ioc_should_update_resolve_dependency_strategy():
        was_called: bool = False

        def dependency(*args):
            nonlocal was_called
            was_called = True
            return args

        default_strategy = Ioc.strategy
        Ioc.resolve("Update Ioc Resolve Dependency Strategy", ActionBase, dependency).execute()
        Ioc.strategy = default_strategy

        assert was_called

    @staticmethod
    @pytest.mark.skip(reason="Доработать, т.к. выполнение InitAction() ломает тест")
    def test_ioc_should_throw_value_error_exception_if_dependency_is_not_found():
        with pytest.raises(ValueError):
            Ioc.resolve("UnexistingDependency", ActionBase).execute()

    @staticmethod
    @pytest.mark.skip(reason="Доработать, т.к. выполнение InitAction() ломает тест")
    def test_ioc_should_throw_invalid_cast_exception_if_dependency_resolves_another_type():
        with pytest.raises(TypeError):
            Ioc.resolve("Update Ioc Resolve Dependency Strategy", str, lambda *args: args)

    @staticmethod
    def test_dependency_not_found_in_default_strategy_raises():
        with pytest.raises(ValueError):
            Ioc._raise_dependency_not_found("missing_dependency")

    @staticmethod
    def test_resolved_object_of_wrong_type_raises():
        Ioc.resolve("IoC.Register", ActionBase, "Test.Wrong.Type", lambda: "not an int").execute()
        with pytest.raises(TypeError):
            Ioc.resolve("Test.Wrong.Type", int)

    @staticmethod
    def test_resolved_object_of_wrong_generic_type_raises():
        Ioc.resolve("IoC.Register", ActionBase, "Test.Wrong.Generic", lambda: "not a list").execute()
        with pytest.raises(TypeError):
            Ioc.resolve("Test.Wrong.Generic", list[int])

    @staticmethod
    def test_resolved_object_of_matching_generic_type_ok():
        Ioc.resolve("IoC.Register", ActionBase, "Test.Right.Generic", lambda: [1, 2, 3]).execute()
        assert Ioc.resolve("Test.Right.Generic", list[int]) == [1, 2, 3]
