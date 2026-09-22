import pytest
from flask import Flask, jsonify
from pydantic import BaseModel

from src.space_battle.models import validate_pydantic as validate_from_package
from src.space_battle.models.validation import validate_pydantic as validate_from_module


class PayloadModel(BaseModel):
    name: str
    age: int


def _build_app(validate):
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.post("/echo", endpoint="echo")
    @validate(PayloadModel)
    def echo(request):
        return jsonify({"name": request.name, "age": request.age}), 200

    @app.post("/boom", endpoint="boom")
    @validate(PayloadModel)
    def boom(request):
        raise RuntimeError("boom")

    return app


@pytest.fixture(params=[validate_from_package, validate_from_module], ids=["package", "module"])
def app(request):
    return _build_app(request.param)


class TestValidatePydantic:
    @staticmethod
    def test_valid_payload(app):
        with app.test_client() as client:
            response = client.post("/echo", json={"name": "neo", "age": 30})
        assert response.status_code == 200
        assert response.get_json() == {"name": "neo", "age": 30}

    @staticmethod
    def test_empty_body_returns_400(app):
        with app.test_client() as client:
            response = client.post("/echo", json={})
        assert response.status_code == 400
        assert response.get_json()["status"] == "error"
        assert "Empty request" in response.get_json()["message"]

    @staticmethod
    def test_non_json_content_type_returns_400(app):
        with app.test_client() as client:
            response = client.post("/echo", data="not json", content_type="text/plain")
        assert response.status_code == 400

    @staticmethod
    def test_validation_error_returns_400(app):
        with app.test_client() as client:
            response = client.post("/echo", json={"name": "neo"})
        assert response.status_code == 400
        assert response.get_json()["status"] == "error"
        assert "Validation error" in response.get_json()["message"]

    @staticmethod
    def test_handler_exception_returns_400(app):
        with app.test_client() as client:
            response = client.post("/boom", json={"name": "neo", "age": 30})
        assert response.status_code == 400
        assert response.get_json()["status"] == "error"
        assert "Error: boom" in response.get_json()["message"]
