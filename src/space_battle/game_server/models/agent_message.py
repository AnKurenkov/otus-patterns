from typing import Any, Dict

from pydantic import BaseModel, Field


class AgentMessageModel(BaseModel):
    """Модель для входящих сообщений от агента"""

    agent_id: str = Field(..., description="Уникальный идентификатор агента")
    game_id: str = Field(..., description="Уникальный идентификатор игры")
    object_id: str = Field(..., description="Уникальный идентификатор игрового объекта")
    action_id: str = Field(..., description="Уникальный идентификатор действия над игровым объектом")
    data: Dict[str, Any] = Field(default_factory=dict, description="Данные сообщения")
