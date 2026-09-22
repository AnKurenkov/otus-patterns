from src.space_battle.core.objects.game_object_base import GameObjectBase
from src.space_battle.core.objects.missile import Missile


class TestGameObjectBase:
    def test_type_property(self):
        obj = GameObjectBase("obj-1", "spaceship", {"Movable"})
        assert obj.type == "spaceship"

    def test_capabilities_empty_by_default(self):
        obj = GameObjectBase("obj-1", "test")
        assert obj.capabilities == set()


class TestMissile:
    def test_init(self):
        missile = Missile("missile-1")
        assert missile.id == "missile-1"
        assert missile.type == "missile"
        assert missile.capabilities == {"Movable", "Fuelable"}
