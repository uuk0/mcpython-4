"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals
import gui.ItemStack
import gui.Slot
import chat.Chat
import util.math
import traceback
import ResourceLocator
import mod.ModMcpython


class Player:
    GAMEMODE_DICT: dict = {
        "survival": 0, "0": 0,
        "creative": 1, "1": 1,
        "adventure": 2, "2": 2,
        "spectator": 3, "3": 3
    }

    def __init__(self, name):
        globals.player = self

        self.name: str = name
        self.gamemode: int = -1
        self.set_gamemode(1)
        self.hearts: int = 20
        self.hunger: int = 20
        self.xp: int = 0
        self.xp_level: int = 0
        self.armor_level = 0
        self.armor_toughness = 0

        self.fallen_since_y = -1 

        self.inventorys: dict = {}

        self.inventory_order: list = [  # an ([inventoryindexname: str], [reversed slots: bool}) list
            ("hotbar", False),
            ("main", False)
        ]

        self.active_inventory_slot: int = 0

        self.iconparts = []

        mod.ModMcpython.mcpython.eventbus.subscribe("stage:inventories", self.create_inventories,
                                                    info="setting up player inventory")

    def create_inventories(self):
        import gui.InventoryPlayerHotbar
        import gui.InventoryPlayerMain

        hotbar = self.inventorys['hotbar'] = gui.InventoryPlayerHotbar.InventoryPlayerHotbar()
        self.inventorys['main'] = gui.InventoryPlayerMain.InventoryPlayerMain(hotbar)
        self.inventorys['chat'] = chat.Chat.ChatInventory()

        self.iconparts = [(ResourceLocator.read("build/texture/gui/icons/hart.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hart_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hart_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/hunger.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hunger_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/hunger_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/armor.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/armor_half.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/armor_base.png", "pyglet")),
                          (ResourceLocator.read("build/texture/gui/icons/xp_bar_empty.png", "pyglet"),
                           ResourceLocator.read("build/texture/gui/icons/xp_bar.png", "pyglet"))]

        import block.BlockCraftingTable, gui.InventoryCraftingTable
        block.BlockCraftingTable.BlockCraftingTable.inventory = gui.InventoryCraftingTable.InventoryCraftingTable()

    def set_gamemode(self, gamemode: int or str):
        gamemode = self.GAMEMODE_DICT.get(gamemode, gamemode)
        # if it is a repr of the gamemode, get the int gamemode
        # else, return the int
        if gamemode == 0:
            globals.window.flying = False
        elif gamemode == 1:
            pass
        elif gamemode == 2:
            globals.window.flying = False
        elif gamemode == 3:
            globals.window.flying = True
        else:
            raise ValueError("can't cast {} to valid gamemode".format(gamemode))
        self.gamemode = gamemode

    def get_needed_xp_for_next_level(self) -> int:
        if self.xp_level < 16:
            return self.xp_level * 2 + 5
        elif self.xp_level < 30:
            return 37 + (self.xp_level - 15) * 5
        else:
            return 107 + (self.xp_level - 29) * 9

    def add_xp(self, xp: int):
        while xp > 0:
            if self.xp + xp < self.get_needed_xp_for_next_level():
                self.xp += xp
                return
            elif xp > self.get_needed_xp_for_next_level():
                xp -= self.get_needed_xp_for_next_level()
                self.xp_level += 1
            else:
                xp = xp - (self.get_needed_xp_for_next_level() - self.xp)
                self.xp_level += 1

    def add_xp_level(self, xp_levels: int):
        self.xp_level += xp_levels

    def add_to_free_place(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        adds the item onto the itemstack
        :param itemstack: the itemstack to add
        :return: either successful or not
        """
        if not itemstack.item or itemstack.amount == 0:
            return True
        for inventory_name, reverse in self.inventory_order:
            inventory = self.inventorys[inventory_name]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if slot.itemstack.item and slot.itemstack.item.get_name() == itemstack.item.get_name() and \
                        slot.interaction_mode[2]:
                    if slot.itemstack.item and slot.itemstack.amount + itemstack.amount <= itemstack.item. \
                            get_max_stack_size():
                        slot.itemstack.amount += itemstack.amount
                        return True
                    else:
                        m = slot.itemstack.item.get_max_stack_size()
                        delta = m - slot.itemstack.amount
                        slot.itemstack.amount = m
                        itemstack.amount -= delta
                if itemstack.amount <= 0:
                    return True
        for inventory_name, reverse in self.inventory_order:
            inventory = self.inventorys[inventory_name]
            slots = inventory.slots
            if reverse:
                slots.reverse()
            for slot in slots:
                if not slot.itemstack.item and slot.interaction_mode[2]:
                    slot.itemstack = itemstack
                    return True
        return False

    def set_active_inventory_slot(self, slot: int):
        self.active_inventory_slot = slot

    def get_active_inventory_slot(self):
        return self.inventorys["hotbar"].slots[self.active_inventory_slot]

    def kill(self, test_totem=True):
        if test_totem:
            if self.get_active_inventory_slot().itemstack.get_item_name() == "minecraft:totem_of_undying":
                self.get_active_inventory_slot().itemstack.clean()
                self.hearts = 20
                self.hunger = 20
                return
            elif self.inventorys["main"].slots[45].itemstack.get_item_name() == "minecraft:totem_of_undying":
                self.inventorys["main"].slots[45].itemstack.clean()
                self.hearts = 20
                self.hunger = 20
                return
        globals.commandparser.parse("/clear")
        print("[CHAT] player {} died".format(self.name))
        self.position = (0, util.math.get_max_y((0,0,0)), 0)
        self.active_inventory_slot = 0
        globals.window.dy = 0
        globals.chat.close()
        self.xp = 0
        self.xp_level = 0
        self.hearts = 20
        self.hunger = 20
        globals.window.flying = False
        self.armor_level = 0
        self.armor_toughness = 0
        # todo: recalculate armor level!

    def _get_position(self):
        return globals.window.position

    def _set_position(self, position):
        globals.window.position = position

    position = property(_get_position, _set_position)

    def damage(self, hearts: int, check_gamemode=True):
        """
        damage the player and removes the given amount of hearts (two hearts are one full displayed hart)
        """
        hearts = hearts * (1 - min([20, max([self.armor_level / 5, self.armor_level -
                                             hearts / (2 + self.armor_toughness / 4)])]))
        if self.gamemode in [0, 2] or not check_gamemode:
            self.hearts -= hearts
            if self.hearts <= 0:
                self.kill()
