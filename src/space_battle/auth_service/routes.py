import time
import uuid

import jwt
from flask import Blueprint, jsonify

from src.space_battle.auth_service.models import GameRequestModel, TokenRequestModel
from src.space_battle.auth_service.storage import GameRepository
from src.space_battle.config import settings
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction
from src.space_battle.core.scopes.thread_scope_context import ThreadScopeContext
from src.space_battle.models import ResponseModel, validate_pydantic

router = Blueprint("auth", __name__)


@router.before_request
def ensure_application_scope():
    if ThreadScopeContext.get_current_scope() is None:
        InitializeApplicationScopeAction().execute()

    from src.space_battle.auth_service.dependencies import RegisterAuthServiceDependenciesAction

    RegisterAuthServiceDependenciesAction().execute()


@router.post("/game")
@validate_pydantic(GameRequestModel)
def create_game(request: GameRequestModel):
    repository = Ioc.resolve("GameRepository", GameRepository)
    game_id = str(uuid.uuid4())
    repository.create(game_id, request.participants)
    response = ResponseModel(
        status="created",
        message="Game with 'game_id' created.",
        data={"game_id": game_id},
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 201


@router.post("/auth/token")
@validate_pydantic(TokenRequestModel)
def get_token(request: TokenRequestModel):
    repository = Ioc.resolve("GameRepository", GameRepository)

    if not repository.exists(request.game_id):
        response = ResponseModel(
            status="error",
            message="Game not found.",
            data={},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 404

    participants = repository.get_participants(request.game_id)
    if request.user_id not in participants:
        response = ResponseModel(
            status="error",
            message="User is not a participant of this game.",
            data={},
            request_id=str(uuid.uuid4()),
        )
        return jsonify(response.model_dump()), 403

    payload = {
        "sub": request.user_id,
        "game_id": request.game_id,
        "exp": int(time.time()) + settings.token_expiration_seconds,
    }
    # Подписываем токен
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    response = ResponseModel(
        status="success",
        message="",
        data={"access_token": token, "token_type": "bearer"},
        request_id=str(uuid.uuid4()),
    )
    return jsonify(response.model_dump()), 200
