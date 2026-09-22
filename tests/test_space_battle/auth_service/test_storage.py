import pytest

from src.space_battle.auth_service.storage import (
    GameRepository,
    InMemoryGameRepository,
    create_game_repository,
    register_backend,
)
from src.space_battle.config import settings


class TestInMemoryGameRepository:
    @staticmethod
    def test_create_and_exists():
        repository = InMemoryGameRepository()
        assert repository.exists("game-1") is False

        repository.create("game-1", ["user_1", "user_2"])
        assert repository.exists("game-1") is True

    @staticmethod
    def test_get_participants():
        repository = InMemoryGameRepository()
        repository.create("game-1", ["user_1", "user_2"])

        assert repository.get_participants("game-1") == ["user_1", "user_2"]

    @staticmethod
    def test_get_participants_missing_game_returns_none():
        repository = InMemoryGameRepository()
        assert repository.get_participants("game-1") is None

    @staticmethod
    def test_clear():
        repository = InMemoryGameRepository()
        repository.create("game-1", ["user_1"])
        repository.clear()

        assert repository.exists("game-1") is False


class TestCreateGameRepository:
    @staticmethod
    def test_returns_in_memory_backend_by_default():
        assert isinstance(create_game_repository(), InMemoryGameRepository)

    @staticmethod
    def test_returns_singleton():
        assert create_game_repository() is create_game_repository()

    @staticmethod
    def test_unknown_backend_raises(monkeypatch):
        monkeypatch.setattr(settings, "storage_backend", "no-such-backend")
        with pytest.raises(ValueError, match="no-such-backend"):
            create_game_repository()

    @staticmethod
    def test_custom_backend_can_be_registered(monkeypatch):
        class FakeRepository(GameRepository):
            def create(self, game_id, participants):
                pass

            def exists(self, game_id):
                return False

            def get_participants(self, game_id):
                return None

        register_backend("fake", FakeRepository)
        monkeypatch.setattr(settings, "storage_backend", "fake")

        repository = create_game_repository()
        assert isinstance(repository, FakeRepository)
        assert create_game_repository() is repository
