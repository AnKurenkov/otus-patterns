from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.commands import RegisterGameCommandsAction
from src.space_battle.core.adapters.actions.create_adapter_action import IocRegisterCreateAdapterAction
from src.space_battle.core.adapters.actions.fuelable_adapter_actions import IocRegisterFuelableAction
from src.space_battle.core.adapters.actions.movable_adapter_actions import IocRegisterMovableAction
from src.space_battle.core.adapters.actions.rotatable_adapter_actions import IocRegisterRotatableAction
from src.space_battle.core.init.init_object_factories import RegisterGameObjectFactoriesInitAction


class RegisterGameDependenciesAction(ActionBase):
    """Оркестрирует регистрацию зависимостей игрового движка в IoC."""

    def execute(self):
        IocRegisterMovableAction().execute()
        IocRegisterRotatableAction().execute()
        IocRegisterFuelableAction().execute()
        IocRegisterCreateAdapterAction().execute()
        RegisterGameObjectFactoriesInitAction().execute()
        RegisterGameCommandsAction().execute()
