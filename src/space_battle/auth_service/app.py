import time
import uuid

import jwt
from flask import Flask, jsonify

from src.space_battle.auth_service.models import GameRequestModel, TokenRequestModel
from src.space_battle.config import ALGORITHM, SECRET_KEY
from src.space_battle.models import ResponseModel, validate_pydantic

app = Flask(__name__)

# In-memory хранилище (в продакшене здесь будет БД)
# Формат: {game_id: [user_id_1, user_id_2, ...]}
games_db: dict[str, list[str]] = {}


@app.post("/game")
@validate_pydantic(GameRequestModel)
def create_game(request: GameRequestModel):
    game_id = str(uuid.uuid4())
    games_db[game_id] = request.participants
    response = ResponseModel(
        status="created",
        message="Game with 'game_id' created.",
        data={"game_id": game_id},
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 201


@app.post("/auth/token")
@validate_pydantic(TokenRequestModel)
def get_token(request: TokenRequestModel):
    if request.game_id not in games_db:
        response = ResponseModel(
            status="error",
            message="Game not found.",
            data={},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 404

    if request.user_id not in games_db[request.game_id]:
        response = ResponseModel(
            status="error",
            message="User is not a participant of this game.",
            data={},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 403

    payload = {"sub": request.user_id, "game_id": request.game_id, "exp": int(time.time()) + 3600}
    # Подписываем токен
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    response = ResponseModel(
        status="success",
        message="",
        data={"access_token": token, "token_type": "bearer"},
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
