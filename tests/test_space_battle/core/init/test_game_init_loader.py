import json

import pytest

from src.space_battle.core.init.game_init_exception import GameInitError
from src.space_battle.core.init.game_init_loader import load_initial_from_json


class TestGameInitLoader:
    @staticmethod
    def test_load_from_json_string():
        data = {"id": "game-1", "objects": []}
        loaded = load_initial_from_json(json.dumps(data))
        assert loaded == data

    @staticmethod
    def test_load_from_file(tmp_path):
        file = tmp_path / "game.json"
        data = {"id": "game-1", "objects": [], "field": {"width": 10, "height": 10}}
        file.write_text(json.dumps(data), encoding="utf-8")
        assert load_initial_from_json(file) == data

    @staticmethod
    def test_load_broken_json_raises():
        with pytest.raises(GameInitError):
            load_initial_from_json("{broken json")

    @staticmethod
    def test_load_non_dict_root_raises():
        with pytest.raises(GameInitError):
            load_initial_from_json("[1, 2, 3]")

    @staticmethod
    def test_load_missing_file_treated_as_json_raises():
        with pytest.raises(GameInitError):
            load_initial_from_json("definitely_missing_folder/no_such_game.json")
