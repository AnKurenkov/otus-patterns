from pydantic import BaseModel


class GameCreateModel(BaseModel):
    """Модель запроса на создание игры"""

    participants: list[str]
