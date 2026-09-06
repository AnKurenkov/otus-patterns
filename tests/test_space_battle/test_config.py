import os
from typing import Any

import pytest

from src.space_battle.config import Settings, settings
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.scopes.app_scope import (
    ApplicationScopeError,
    get_application_scope,
    initialize_application_scope,
)


@pytest.fixture
def clear_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("SPACE_BATTLE_"):
            monkeypatch.delenv(key, raising=False)


class TestSettings:
    @staticmethod
    def test_defaults(clear_env):
        fresh = Settings(_env_file=None)
        assert fresh.secret_key == "super_secret_key_for_space_battle_2026"
        assert fresh.algorithm == "HS256"
        assert fresh.game_service_host == "0.0.0.0"
        assert fresh.game_service_port == 8001
        assert fresh.auth_service_host == "0.0.0.0"
        assert fresh.auth_service_port == 8002
        assert fresh.token_expiration_seconds == 3600

    @staticmethod
    def test_env_override(monkeypatch):
        monkeypatch.setenv("SPACE_BATTLE_GAME_SERVICE_PORT", "9101")
        monkeypatch.setenv("SPACE_BATTLE_AUTH_SERVICE_HOST", "127.0.0.1")
        monkeypatch.setenv("SPACE_BATTLE_TOKEN_EXPIRATION_SECONDS", "120")
        monkeypatch.setenv("SPACE_BATTLE_SECRET_KEY", "custom_secret")
        fresh = Settings(_env_file=None)
        assert fresh.game_service_port == 9101
        assert fresh.auth_service_host == "127.0.0.1"
        assert fresh.token_expiration_seconds == 120
        assert fresh.secret_key == "custom_secret"


class TestApplicationScope:
    @staticmethod
    def test_config_resolvable_via_ioc():
        resolved = Ioc.resolve("Config", Settings)
        assert resolved is settings

    @staticmethod
    def test_config_resolvable_from_child_scope():
        previous_scope = Ioc.resolve("IoC.Scope.Current", Any)
        child_scope = Ioc.resolve("IoC.Scope.Create", Any)
        Ioc.resolve("IoC.Scope.Current.Set", ActionBase, child_scope).execute()
        try:
            resolved = Ioc.resolve("Config", Settings)
            assert resolved is settings
        finally:
            Ioc.resolve("IoC.Scope.Current.Set", ActionBase, previous_scope).execute()

    @staticmethod
    def test_get_application_scope_returns_initialized_scope():
        assert get_application_scope() is not None

    @staticmethod
    def test_get_application_scope_raises_without_init(monkeypatch):
        monkeypatch.setattr("src.space_battle.core.scopes.app_scope._APPLICATION_SCOPE", None)
        with pytest.raises(ApplicationScopeError):
            get_application_scope()

    @staticmethod
    def test_initialize_application_scope_is_reusable():
        scope = initialize_application_scope()
        assert get_application_scope() is scope
