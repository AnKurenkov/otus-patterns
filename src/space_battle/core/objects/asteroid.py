from src.space_battle.core.objects.game_object_base import GameObjectBase


class Asteroid(GameObjectBase):
    """Астероид: движется, не управляется, топлива нет.

    Может быть разрушен попаданием ракеты (атрибут health).
    """

    CAPABILITIES = {"Movable", "Destroyable"}

    def __init__(self, obj_id: str):
        super().__init__(obj_id, "asteroid", self.CAPABILITIES)
        self.set_property("health", 1)
