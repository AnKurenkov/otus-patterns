from typing import Type

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Destroyable, Fuelable, Movable, Rotatable


class RegisterCapabilitiesInitAction(ActionBase):
    """Регистрирует типы способностей: "Game.Init.Capability.<имя>"."""

    def execute(self):
        register_capability("Movable", Movable)
        register_capability("Rotatable", Rotatable)
        register_capability("Fuelable", Fuelable)
        register_capability("Destroyable", Destroyable)


def register_capability(capability_name: str, capability_type: Type):
    """Регистрация типа способности (расширение набора способностей)."""
    Ioc.resolve(
        "IoC.Register",
        ActionBase,
        f"Game.Init.Capability.{capability_name}",
        lambda: capability_type,
    ).execute()
