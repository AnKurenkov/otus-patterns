from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Fuelable


class IocRegisterFuelableAction(ActionBase):
    def execute(self):
        Ioc.resolve(
            "IoC.Register", ActionBase, "Fuelable.fuel.Get", lambda obj: FuelableFuelGetAction(obj).execute()
        ).execute()
        Ioc.resolve(
            "IoC.Register", ActionBase, "Fuelable.fuel.Set", lambda obj, fuel: FuelableFuelSetAction(obj, fuel)
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Fuelable.fuel_consumption.Get",
            lambda obj: FuelableFuelConsumptionGetAction(obj).execute(),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Fuelable.fuel_consumption.Set",
            lambda obj, fuel_consumption: FuelableFuelConsumptionSetAction(obj, fuel_consumption),
        ).execute()


class FuelableFuelGetAction(ActionBase):
    def __init__(self, obj: Fuelable):
        self._obj = obj

    def execute(self) -> int:
        return self._obj.get_property("fuel")


class FuelableFuelSetAction(ActionBase):
    def __init__(self, obj: Fuelable, fuel: int):
        self._obj = obj
        self._fuel = fuel

    def execute(self):
        self._obj.set_property("fuel", self._fuel)


class FuelableFuelConsumptionGetAction(ActionBase):
    def __init__(self, obj: Fuelable):
        self._obj = obj

    def execute(self) -> int:
        return self._obj.get_property("fuel_consumption")


class FuelableFuelConsumptionSetAction(ActionBase):
    def __init__(self, obj: Fuelable, fuel_consumption: int):
        self._obj = obj
        self._fuel_consumption = fuel_consumption

    def execute(self):
        self._obj.set_property("fuel_consumption", self._fuel_consumption)
