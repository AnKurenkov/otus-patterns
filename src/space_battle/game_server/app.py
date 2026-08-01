import uuid
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request

from src.space_battle.config import ALGORITHM, SECRET_KEY
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.interpret_action import InterpretAction
from src.space_battle.game_server.models import AgentMessageModel
from src.space_battle.models import ResponseModel, validate_pydantic

app = Flask(__name__)


def check_jwt_token(f):
    """
    Декоратор проверки JWT:
    1. Проверяет подпись (хэш) и срок жизни токена.
    2. Проверяет, что game_id в токене совпадает с game_id из запроса.
    3. Кладёт декодированный токен в g для использования в обработчике при необходимости.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            response = ResponseModel(
                status="error",
                message="Invalid authorization header.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 401

        token = auth_header.split(" ", 1)[1]

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            response = ResponseModel(
                status="error",
                message="Token has expired.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 401
        except jwt.PyJWTError:
            response = ResponseModel(
                status="error",
                message="Invalid token signature.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 401

        game_id_from_request = kwargs.get("game_id")
        if decoded_token.get("game_id") != game_id_from_request:
            response = ResponseModel(
                status="error",
                message="Token is not valid for this specific game.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 403

        g.decoded_token = decoded_token
        return f(*args, **kwargs)

    return wrapper


@app.route("/api/message", methods=["POST"])
@check_jwt_token
@validate_pydantic(AgentMessageModel)
def receive_message(message: AgentMessageModel):
    """
    Endpoint для приёма входящих сообщений от Агентов.
    Тело запроса — JSON в формате AgentMessageModel.
    """
    try:
        cmd = InterpretAction(message)  # TODO: Брать из IoC
        game = game_router.get(message.game_id)
        game.queue.put(cmd)
    except Exception as e:
        response = ResponseModel(
            status="error",
            message=f"Processing error: {str(e)}",
            data={"accepted": False, "agent": message.agent_id, "game": message.game_id},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 404

    response = ResponseModel(
        status="accepted",
        message=f"Message from agent {message.agent_id} for game {message.game_id} accepted",
        data={
            "accepted": True,
            "agent_id": message.agent_id,
            "game_id": message.game_id,
            "object_id": message.object_id,
            "action_id": message.action_id,
        },
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
