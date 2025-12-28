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
