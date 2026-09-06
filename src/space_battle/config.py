# Конфигурация Space Battle.
#
# Всё, что может меняться в рантайме (JWT-секрет, алгоритм, хосты/порты сервисов,
# срок жизни токена), выносится в переменные окружения с префиксом SPACE_BATTLE_
# и/или файл .env в корне проекта. Смена конфигурации не требует правки исходников.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаются из окружения и/или файла .env."""

    model_config = SettingsConfigDict(
        env_prefix="SPACE_BATTLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Секретный ключ для подписи JWT. Должен быть одинаковым на обоих сервисах.
    secret_key: str = "super_secret_key_for_space_battle_2026"
    algorithm: str = "HS256"

    # Game Service
    game_service_host: str = "0.0.0.0"
    game_service_port: int = 8001

    # Auth Service
    auth_service_host: str = "0.0.0.0"
    auth_service_port: int = 8002

    # Срок жизни JWT-токена в секундах
    token_expiration_seconds: int = 3600


# Модульный синглтон. Команды движка получают его через IoC-зависимость "Config"
# (см. InitializeApplicationScopeAction в core/scopes/init_app_scope_action.py), а не прямым импортом.
settings = Settings()
