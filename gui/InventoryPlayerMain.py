"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import gui.Slot
import gui.ItemStack
import crafting.CraftingHandler
import crafting.GridRecipeInterface
import item.ItemArmor


class InventoryPlayerMain(gui.Inventory.Inventory):
    """
    inventory class for the main part of the inventory
    """

    def __init__(self, hotbar):
        self.hotbar = hotbar
        super().__init__()

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/playerinventorymain.json"

    def on_create(self):
        inputs = [self.slots[40:42], self.slots[42:44]]
        self.recipeinterface = crafting.GridRecipeInterface.GridRecipeInterface(inputs, self.slots[44])

    def create_slots(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        return [self.hotbar.slots[i].copy() for i in range(9)] + \
               [gui.Slot.Slot() for _ in range(27)] + \
               [gui.Slot.Slot(allow_player_add_to_free_place=False, on_update=self.armor_update) for _ in range(4)] + \
               [gui.Slot.Slot(allow_player_add_to_free_place=False) for _ in range(6)]

    def on_activate(self):
        pass

    def armor_update(self, player=None):
        # todo: add toughness
        points = 0
        for slot in self.slots[35:40]:
            if slot.itemstack.item:
                if issubclass(type(slot.itemstack.item), item.ItemArmor.ItemArmor):
                    points += slot.itemstack.item.getDefensePoints()
        G.player.armor_level = points

    def on_deactivate(self):
        for slot in self.slots[40:45]:
            slot: gui.Slot.Slot
            itemstack = slot.itemstack
            slot.itemstack = gui.ItemStack.ItemStack.get_empty()
            G.player.add_to_free_place(itemstack)
        self.slots[45].itemstack.clean()

