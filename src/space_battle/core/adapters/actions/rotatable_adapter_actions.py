from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Rotatable
from src.space_battle.core.space import Direction


class IocRegisterRotatableAction(ActionBase):
    def execute(self):
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Rotatable.direction.Get",
            lambda obj: RotatableDirectionGetAction(obj).execute(),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Rotatable.direction.Set",
            lambda obj, direction: RotatableDirectionSetAction(obj, direction),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Rotatable.angular_velocity.Get",
            lambda obj: RotatableAngularVelocityGetAction(obj).execute(),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Rotatable.angular_velocity.Set",
            lambda obj, angular_velocity: RotatableAngularVelocitySetAction(obj, angular_velocity),
        ).execute()


class RotatableDirectionGetAction(ActionBase):
    def __init__(self, obj: Rotatable):
        self._obj = obj

    def execute(self) -> Direction:
        return self._obj.get_property("direction")


class RotatableDirectionSetAction(ActionBase):
    def __init__(self, obj: Rotatable, direction: Direction):
        self._obj = obj
        self._direction = direction

    def execute(self):
        self._obj.set_property("direction", self._direction)


class RotatableAngularVelocityGetAction(ActionBase):
    def __init__(self, obj: Rotatable):
        self._obj = obj

    def execute(self) -> int:
        return self._obj.get_property("angular_velocity")


class RotatableAngularVelocitySetAction(ActionBase):
    def __init__(self, obj: Rotatable, angular_velocity: int):
        self._obj = obj
        self._angular_velocity = angular_velocity

    def execute(self):
        self._obj.set_property("angular_velocity", self._angular_velocity)
