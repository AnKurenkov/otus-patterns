from typing import Any, Callable, TypeVar, cast

from src.space_battle.core.actions.base import ActionBase

T = TypeVar("T")


class Ioc:
    """
    Контейнер инверсии зависимостей (Расширяемая фабрика).
    """

    strategy: Callable[[str, list[Any]], Any] = staticmethod(
        lambda dependency, args: (
            UpdateIocResolveDependencyStrategyAction(
                args[0]  # Callable[[Callable[[str, list[Any]], Any]], Callable[[str, list[Any]], Any]]
            )
            if dependency == "Update Ioc Resolve Dependency Strategy"
            else Ioc._raise_dependency_not_found(dependency)
        )
    )

    @staticmethod
    def _raise_dependency_not_found(dependency: str):
        raise ValueError(f"Dependency '{dependency}' is not found.")

    @staticmethod
    def resolve(dependency: str, expected_type: type[T], *args: Any) -> T:
        """
        Разрешение зависимости по имени.
        :param dependency: Строковое имя зависимости. В реализации контейнера
        по умолчанию определена только одна зависимость "Update Ioc Resolve Dependency Strategy",
        которая позволяет переопределить стратегию разрешения зависимостей по-умолчанию.
        :param args: Произвольные аргументы для стратегии.
        Для переопределения стратегии разрешения зависимостей по-умолчанию
        на вход подается лямбда функция типа Func<Func<string, object[], object>, Func<string, object[], object> >,
        которая на вход принимает текущую стратегию разрешения зависимостей типа Func<string, object[], object>,
        на выходе возвращает новую стратегию типа Func<string, object[], object>.
        :param expected_type: Ожидаемый тип зависимости. Если тип зависимости не соответствует ожидаемой,
        то выбрасывается исключение.
        :return: Объект, соответствующий зависимости (приведённый к типу T).
        Если полученный объект невозможно привести в запрашиваемому типу или указана несуществующая зависимость,
        то выбрасывается исключение.
        """
        obj = Ioc.strategy(dependency, args)
        if not isinstance(obj, expected_type):
            raise TypeError(f"Resolved object for '{dependency}' is of type {type(obj)}, but expected {expected_type}")
        return cast(T, obj)


class UpdateIocResolveDependencyStrategyAction(ActionBase):
    def __init__(self, updater: Callable[[Callable[[str, list[Any]], Any]], Callable[[str, list[Any]], Any]]):
        self._update_ioc_strategy = updater

    def execute(self):
        Ioc.strategy = self._update_ioc_strategy(Ioc.strategy)
