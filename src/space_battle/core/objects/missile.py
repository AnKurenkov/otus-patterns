from src.space_battle.core.objects.game_object_base import GameObjectBase


class Missile(GameObjectBase):
    """Ракета/снаряд: движется прямолинейно, имеет запас топлива.

    Появляется на поле при применении команды Fire.
    """

    CAPABILITIES = {"Movable", "Fuelable"}

    def __init__(self, obj_id: str):
        super().__init__(obj_id, "missile", self.CAPABILITIES)
