import requests

from src.space_battle.config import settings


class AuthServiceError(Exception):
    """Ошибка при обращении к Auth Service"""


def register_game(participants: list[str]) -> str:
    """Создаёт игру в Auth Service и возвращает её game_id."""
    try:
        response = requests.post(
            f"{settings.auth_service_url}/game",
            json={"participants": participants},
            timeout=10,
        )
    except requests.RequestException as e:
        raise AuthServiceError(f"Cannot reach Auth Service: {e}") from e

    if response.status_code != 201:
        raise AuthServiceError(f"Auth Service returned status {response.status_code}: {response.text}")

    data = response.json()
    try:
        return data["data"]["game_id"]
    except (KeyError, TypeError) as e:
        raise AuthServiceError(f"Unexpected Auth Service response: {data}") from e
