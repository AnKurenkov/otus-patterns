from pydantic import BaseModel


class GameRequestModel(BaseModel):
    participants: list[str]
