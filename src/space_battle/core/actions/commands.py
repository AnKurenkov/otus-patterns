from src.space_battle.core.actions.actions import BurnFuel, CheckFuel, Move, Rotate
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.macro_actions import MoveWithBurnFuel
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.objects.capabilities import Fuelable, Movable, Rotatable


class RegisterGameCommandsAction(ActionBase):
    """Регистрирует игровые команды в IoC по их action_id."""

    def execute(self):
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Move",
            lambda obj, data: Move(Ioc.resolve("Adapter", Movable, Movable, obj)),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "Rotate",
            lambda obj, data: Rotate(Ioc.resolve("Adapter", Rotatable, Rotatable, obj)),
        ).execute()
        Ioc.resolve(
            "IoC.Register",
            ActionBase,
            "MoveWithBurnFuel",
            lambda obj, data: MoveWithBurnFuel(
                (
                    CheckFuel(Ioc.resolve("Adapter", Fuelable, Fuelable, obj)),
                    Move(Ioc.resolve("Adapter", Movable, Movable, obj)),
                    BurnFuel(Ioc.resolve("Adapter", Fuelable, Fuelable, obj)),
                )
            ),
        ).execute()
