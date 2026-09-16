import uuid
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify
from flask import request as request_

from src.space_battle.config import settings
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.interpret_action import InterpretAction
from src.space_battle.game_server.auth_client import AuthServiceError, register_game
from src.space_battle.game_server.game_runtime import get_game_runtime
from src.space_battle.game_server.models import AgentMessageModel, GameCreateModel
from src.space_battle.models import ResponseModel, validate_pydantic

router = Blueprint("game", __name__)


@router.before_request
def set_application_scope():
    from src.space_battle.core.scopes.thread_scope_context import ThreadScopeContext

    if ThreadScopeContext.get_current_scope() is None:
        InitializeApplicationScopeAction().execute()


@router.post("/api/game/create")
@validate_pydantic(GameCreateModel)
def create_game(request: GameCreateModel):
    """
    Endpoint для создания новой игры.
    Тело запроса — JSON в формате GameCreateModel (список участников).
    Игра регистрируется в Auth Service и в game_router.
    """
    try:
        game_id = register_game(request.participants)
    except AuthServiceError as e:
        response = ResponseModel(
            status="error",
            message=str(e),
            data={"created": False, "participants": request.participants},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 502

    get_game_runtime().create_game({"id": game_id})

    response = ResponseModel(
        status="created",
        message="Game with 'game_id' created.",
        data={"game_id": game_id, "participants": request.participants},
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 201


def check_jwt_token(f):
    """
    Декоратор проверки JWT:
    1. Проверяет подпись (хэш) и срок жизни токена.
    2. Проверяет, что game_id в токене совпадает с game_id из запроса.
    3. Кладёт декодированный токен в g для использования в обработчике при необходимости.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request_.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            response = ResponseModel(
                status="error",
                message="Invalid authorization header.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 401

        token = auth_header.split(" ", 1)[1]

        try:
            decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
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

        game_id_from_request = request_.json.get("game_id")
        if decoded_token.get("game_id") != game_id_from_request:
            response = ResponseModel(
                status="error",
                message="Token is not valid for this specific game.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 403

        agent_id_from_request = request_.json.get("agent_id")
        if decoded_token.get("sub") != agent_id_from_request:
            response = ResponseModel(
                status="error",
                message="Agent ID does not match token subject.",
                request_id=str(uuid.uuid4()),
            )
            return jsonify(response.model_dump()), 403

        g.decoded_token = decoded_token
        return f(*args, **kwargs)

    return wrapper


@router.route("/api/message", methods=["POST"])
@check_jwt_token
@validate_pydantic(AgentMessageModel)
def receive_message(request: AgentMessageModel):
    """
    Endpoint для приёма входящих сообщений от Агентов.
    Тело запроса — JSON в формате AgentMessageModel.
    """
    try:
        cmd = InterpretAction(request, agent_id=g.decoded_token["sub"])
        game = game_router.get(request.game_id)
        game.queue.put(cmd)
    except Exception as e:
        response = ResponseModel(
            status="error",
            message=f"Processing error: {str(e)}",
            data={"accepted": False, "agent": request.agent_id, "game": request.game_id},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 404

    response = ResponseModel(
        status="accepted",
        message=f"Message from agent {request.agent_id} for game {request.game_id} accepted",
        data={
            "accepted": True,
            "agent_id": request.agent_id,
            "game_id": request.game_id,
            "object_id": request.object_id,
            "action_id": request.action_id,
        },
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 202
