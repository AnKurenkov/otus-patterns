import uuid

from flask import jsonify, request
from pydantic import ValidationError

from src.space_battle.models.response import ResponseModel


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
                                status="error", message="Empty request body.", request_id=str(uuid.uuid4())
                            ).model_dump()
                        ),
                        400,
                    )
                validated_data = model_class(**json_data)
                kwargs["request"] = validated_data
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
