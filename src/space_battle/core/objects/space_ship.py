from src.space_battle.core.objects.game_object_base import GameObjectBase


class SpaceShip(GameObjectBase):
    """Корабль: движется, поворачивается, имеет топливо."""

    CAPABILITIES = {"Movable", "Rotatable", "Fuelable"}

    def __init__(self, obj_id: str):
        super().__init__(obj_id, "spaceship", self.CAPABILITIES)
