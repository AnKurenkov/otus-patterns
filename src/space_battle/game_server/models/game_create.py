from typing import Any, Dict, Optional

from pydantic import BaseModel


class GameCreateModel(BaseModel):
    """Модель запроса на создание игры"""

    participants: list[str]
    config: Optional[Dict[str, Any]] = None
