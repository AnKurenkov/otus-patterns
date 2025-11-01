class SpaceBattleError(Exception):
    """Базовый класс для всех исключений в проекте."""


class GetLocationError(SpaceBattleError):
    """Ошибка получения положения объекта в пространстве."""


class GetVelocityError(SpaceBattleError):
    """Ошибка получения мгновенной скорости объекта в пространстве."""


class ObjectMoveError(SpaceBattleError):
    """Ошибка изменения положения объекта в пространстве."""
