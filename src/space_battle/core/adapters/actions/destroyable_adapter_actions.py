from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Destroyable


class IocRegisterDestroyableAction(ActionBase):
    def execute(self):
        Ioc.resolve(
            "IoC.Register", ActionBase, "Destroyable.health.Get", lambda obj: DestroyableHealthGetAction(obj).execute()
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Destroyable.health.Set",
            lambda obj, health: DestroyableHealthSetAction(obj, health),
        ).execute()


class DestroyableHealthGetAction(ActionBase):
    def __init__(self, obj: Destroyable):
        self._obj = obj

    def execute(self) -> int:
        return self._obj.get_property("health")


class DestroyableHealthSetAction(ActionBase):
    def __init__(self, obj: Destroyable, health: int):
        self._obj = obj
        self._health = health

    def execute(self):
        self._obj.set_property("health", self._health)
