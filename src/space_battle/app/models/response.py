from typing import Any, Dict, Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """Модель ответа сервера"""

    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
