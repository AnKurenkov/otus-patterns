# from operations import register_operations
import uuid

from flask import Flask, jsonify, request
from pydantic import ValidationError

from src.space_battle.app.models.message import MessageModel
from src.space_battle.app.models.response import ResponseModel
from src.space_battle.core.server.game_router import game_router
from src.space_battle.core.server.interpret_action import InterpretAction

app = Flask(__name__)


def validate_pydantic(model_class):
    """Декоратор для валидации Pydantic моделей"""

    def decorator(f):
        def wrapped(*args, **kwargs):
            try:
                json_data = request.get_json()
                if not json_data:
                    return (
                        jsonify(
                            ResponseModel(
                                status="error", message="Empty request body", request_id=str(uuid.uuid4())
                            ).model_dump()
                        ),
                        400,
                    )

                validated_data = model_class(**json_data)
                kwargs["message"] = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                return (
                    jsonify(
                        ResponseModel(
                            status="error", message=f"Validation error: {e.errors()}", request_id=str(uuid.uuid4())
                        ).model_dump()
                    ),
                    400,
                )
            except Exception as e:
                return (
                    jsonify(
                        ResponseModel(
                            status="error", message=f"Error: {str(e)}", request_id=str(uuid.uuid4())
                        ).model_dump()
                    ),
                    400,
                )

        return wrapped

    return decorator


@app.route("/api/message", methods=["POST"])
@validate_pydantic(MessageModel)
def receive_message(message: MessageModel):
    """
    Endpoint для приёма входящих сообщений от Агентов.
    Тело запроса — JSON в формате MessageModel.
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
