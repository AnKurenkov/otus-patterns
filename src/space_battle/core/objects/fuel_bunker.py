from src.space_battle.core.objects.game_object_base import GameObjectBase


class FuelBunker(GameObjectBase):
    """Стационарный источник топлива."""

    CAPABILITIES = {"Fuelable"}

    def __init__(self, obj_id: str):
        super().__init__(obj_id, "fuel_bunker", self.CAPABILITIES)
