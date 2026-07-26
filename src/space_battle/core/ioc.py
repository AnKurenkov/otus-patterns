from typing import Any, Callable, Type, TypeAlias, TypeVar, cast, get_origin

from src.space_battle.core.actions.base import ActionBase

T = TypeVar("T")


Scope: TypeAlias = dict[str, Callable[[list], Any]]
Strategy: TypeAlias = Callable[[str, list[Any]], Any]


class Ioc:
    """
    Контейнер инверсии зависимостей (Расширяемая фабрика).
    """

    _root_scope: Scope = {}
    strategy: Strategy = staticmethod(
        lambda dependency, *args: (
            UpdateIocResolveDependencyStrategyAction(
                args[0]  # Callable[[Callable[[str, list[Any]], Any]], Callable[[str, list[Any]], Any]]
            )
            if dependency == "Update Ioc Resolve Dependency Strategy"
            else Ioc._raise_dependency_not_found(dependency)
        )
    )

    @classmethod
    def get_root_scope(cls) -> dict:
        return cls._root_scope

    @staticmethod
    def _raise_dependency_not_found(dependency: str):
        raise ValueError(f"Dependency '{dependency}' is not found.")

    @classmethod
    def resolve(cls, dependency: str, expected_type: Type[T], *args: Any) -> T:
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
        obj = cls.strategy(dependency, *args)
        if expected_type is not None and expected_type is not Any:
            origin = get_origin(expected_type)
            if origin is None:
                if not isinstance(obj, expected_type):
                    raise TypeError(
                        f"Resolved object for '{dependency}' is of type {type(obj)}, but expected {expected_type}"
                    )
            else:
                if not isinstance(obj, origin):
                    raise TypeError(f"Resolved object for '{dependency}' is of type {type(obj)}, but expected {origin}")
        return cast(T, obj)


class UpdateIocResolveDependencyStrategyAction(ActionBase):
    def __init__(self, updater: Callable[[Callable[[str, list[Any]], Any]], Callable[[str, list[Any]], Any]]):
        self._update_ioc_strategy = updater

    def execute(self):
        Ioc.strategy = self._update_ioc_strategy(Ioc.strategy)
