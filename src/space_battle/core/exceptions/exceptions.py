from src.space_battle.core.exceptions.base import SpaceBattleError


class GetLocationError(SpaceBattleError):
    """Ошибка получения положения объекта в пространстве."""


class GetVelocityError(SpaceBattleError):
    """Ошибка получения мгновенной скорости объекта в пространстве."""


class ObjectMoveError(SpaceBattleError):
    """Ошибка линейного перемещения объекта в пространстве."""


class GetDirectionError(SpaceBattleError):
    """Ошибка получения направления объекта в пространстве."""


class GetAngularVelocityError(SpaceBattleError):
    """Ошибка получения мгновенной угловой скорости объекта в пространстве."""


class ObjectRotateError(SpaceBattleError):
    """Ошибка поворота объекта в пространстве."""
