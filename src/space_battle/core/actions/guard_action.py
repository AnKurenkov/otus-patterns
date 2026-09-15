import logging

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc

logger = logging.getLogger(__name__)


class GuardAction(ActionBase):
    """Команда-защитник: перед выполнением внутренней команды проверяет,
    имеет ли агент (agent_id) право управлять объектом (obj).

    Право проверяется через IoC-зависимость "Game.HasAccess",
    зарегистрированную в скоупе игры. При отказе команда просто игнорируется
    (записывается в лог), внутренняя команда не выполняется.
    """

    def __init__(self, agent_id: str, obj, inner_action: ActionBase):
        self._agent_id = agent_id
        self._obj = obj
        self._inner_action = inner_action

    def execute(self):
        allowed = Ioc.resolve("Game.HasAccess", bool, self._agent_id, self._obj)
        if allowed:
            self._inner_action.execute()
        else:
            logger.info(
                "Команда проигнорирована: агент %s не имеет прав на объект %s (id=%s)",
                self._agent_id,
                getattr(self._obj, "type", "unknown"),
                getattr(self._obj, "id", "unknown"),
            )
