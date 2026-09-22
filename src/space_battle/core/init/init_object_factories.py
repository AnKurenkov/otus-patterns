from typing import Callable

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.asteroid import Asteroid
from src.space_battle.core.objects.fuel_bunker import FuelBunker
from src.space_battle.core.objects.missile import Missile
from src.space_battle.core.objects.space_ship import SpaceShip


class RegisterGameObjectFactoriesInitAction(ActionBase):
    """Регистрирует фабрики игровых объектов по типу: "Game.Init.Object.<type>"."""

    def execute(self):
        register_object_factory("spaceship", lambda obj_id: SpaceShip(obj_id))
        register_object_factory("missile", lambda obj_id: Missile(obj_id))
        register_object_factory("asteroid", lambda obj_id: Asteroid(obj_id))
        register_object_factory("fuel_bunker", lambda obj_id: FuelBunker(obj_id))


def register_object_factory(obj_type: str, factory: Callable[[str], "object"]):
    """Регистрация фабрики объекта (расширение набора типов)."""
    Ioc.resolve("IoC.Register", ActionBase, f"Game.Init.Object.{obj_type}", factory).execute()
