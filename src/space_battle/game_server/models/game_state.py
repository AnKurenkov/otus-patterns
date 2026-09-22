from pydantic import BaseModel


class GameStateRequestModel(BaseModel):
    """Модель запроса на получение состояния игры"""

    game_id: str
    agent_id: str
