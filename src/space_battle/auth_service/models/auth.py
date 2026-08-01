from pydantic import BaseModel


class TokenRequestModel(BaseModel):
    user_id: str
    game_id: str
