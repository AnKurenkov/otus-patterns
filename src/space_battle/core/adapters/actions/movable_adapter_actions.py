from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.base import Movable
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.space import Point, PolarVelocity


class IocRegisterMovableAction(ActionBase):
    def execute(self):
        Ioc.resolve(
            "IoC.Register", ActionBase, "Movable.location.Get", lambda obj: MovableLocationGetAction(obj).execute()
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Movable.location.Set",
            lambda obj, location: MovableLocationSetAction(obj, location),
        ).execute()
        Ioc.resolve(
            "IoC.Register", ActionBase, "Movable.velocity.Get", lambda obj: MovableVelocityGetAction(obj).execute()
        ).execute()


class MovableLocationGetAction(ActionBase):
    def __init__(self, obj: Movable):
        self._obj = obj

    def execute(self) -> Point:
        return getattr(self._obj, "_location")


class MovableLocationSetAction(ActionBase):
    def __init__(self, obj: Movable, location: Point):
        self._obj = obj
        self._location = location

    def execute(self):
        setattr(self._obj, "_location", self._location)


class MovableVelocityGetAction(ActionBase):
    def __init__(self, obj: Movable):
        self._obj = obj

    def execute(self) -> PolarVelocity:
        return getattr(self._obj, "_velocity")
