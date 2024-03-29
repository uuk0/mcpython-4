"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import state.StatePart
import state.StatePartGame
from pyglet.window import key, mouse
import gui.Slot


class OpenedInventoryStatePart(state.StatePart.StatePart):
    """
    class for inventories as state
    todo: make A LOT OF THINGS public
    """

    def __init__(self):
        super().__init__()

        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            G.inventoryhandler.remove_one_from_stack()

    def on_draw_2d(self):
        # import block.BlockCraftingTable
        # print(G.player.inventorys["main"].slots[0].itemstack.get_item_name())
        # print(block.BlockCraftingTable.BlockCraftingTable.inventory.slots[0].itemstack.get_item_name())
        # print(G.player.inventorys["main"].slots[0] == block.BlockCraftingTable.BlockCraftingTable.inventory.slots[0])
        hoveringslot = self._get_slot_for(*G.window.mouse_position)
        if any([inventory.is_blocking_interactions() for inventory in G.inventoryhandler.opened_inventorystack]):
            G.window.set_exclusive_mouse(False)
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = False
        else:
            G.statehandler.update_exclusive()
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = True
        for inventory in G.inventoryhandler.opened_inventorystack:
            inventory.draw(hoveringslot=hoveringslot)
        if G.inventoryhandler.moving_slot.itemstack.item:
            G.inventoryhandler.moving_slot.draw(0, 0)
        G.inventoryhandler.moving_slot.position = G.window.mouse_position

    def _get_slot_for(self, x, y) -> gui.Slot.Slot or None:
        """
        get slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot or None if none found
        """
        for inventory in G.inventoryhandler.opened_inventorystack:
            dx, dy = inventory._get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        # todo: split up into seperated functions / onto an intern event bus
        if G.window.exclusive: return
        slot: gui.Slot.Slot = self._get_slot_for(x, y)
        moving_slot: gui.Slot.Slot = G.inventoryhandler.moving_slot
        if button == mouse.LEFT:
            if slot and (slot.interaction_mode[0] or not slot.itemstack.item) and (slot.interaction_mode[1] or not
                                                                                   moving_slot.itemstack.item):
                if modifiers & key.MOD_SHIFT and slot.on_shift_click:
                    slot.on_shift_click(x, y, button, modifiers)
                else:
                    if slot.itemstack.get_item_name() == moving_slot.itemstack.get_item_name() and \
                            slot.itemstack.get_item_name() is not None:
                        eamount = slot.itemstack.amount
                        ramount = moving_slot.itemstack.amount
                        mstack = slot.itemstack.item.get_max_stack_size()
                        if eamount == mstack: return
                        possible = mstack - eamount
                        if possible > ramount:
                            possible = ramount
                        slot.itemstack.amount += possible
                        slot.call_update(player=True)
                        moving_slot.itemstack.amount -= possible
                        if moving_slot.itemstack.amount <= 0:
                            moving_slot.itemstack.clean()
                    elif slot.allowed_item_tags is None or moving_slot.itemstack.get_item_name() is None or \
                            any([moving_slot.itemstack.get_item_name() in
                                 G.taghandler.taggroups["items"].tags[x].entries for x in slot.allowed_item_tags]):
                        stack, mstack = slot.itemstack, moving_slot.itemstack
                        moving_slot.itemstack = stack
                        slot.set_itemstack(mstack, player=True)
            else:
                # todo: threw the itemstack
                pass
        elif button == mouse.RIGHT:
            if slot:
                if not slot.itemstack.item:
                    if slot.interaction_mode[1] and slot.allowed_item_tags is None or \
                            any([moving_slot.itemstack.get_item_name() in
                                 G.taghandler.taggroups["items"].tags[x].entries for x in slot.allowed_item_tags]):
                        slot.set_itemstack(moving_slot.itemstack.copy().set_amount(1), player=True)
                        moving_slot.itemstack.amount -= 1
                elif not moving_slot.itemstack.item and slot.allow_half_getting:
                    if slot.interaction_mode[0]:
                        moving_slot.itemstack = slot.itemstack.copy()
                        slot.itemstack.amount //= 2
                        moving_slot.itemstack.amount = abs(moving_slot.itemstack.amount - slot.itemstack.amount)
                        if slot.itemstack.amount == 0:
                            slot.itemstack.clean()
                        if moving_slot.itemstack.amount == 0:
                            moving_slot.itemstack.clean()
                        slot.call_update(player=True)
                elif slot.itemstack.item.get_name() == moving_slot.itemstack.item.get_name() and \
                        slot.itemstack.amount < slot.itemstack.item.get_max_stack_size():
                    if slot.interaction_mode[1]:
                        slot.itemstack.amount += 1
                        moving_slot.itemstack.amount -= 1
                        slot.call_update(player=True)
            else:
                # todo: threw one item
                pass
        elif button == mouse.MIDDLE:
            if G.player.gamemode == 1 and slot:
                moving_slot.itemstack = slot.itemstack.copy()
                moving_slot.itemstack.amount = moving_slot.itemstack.item.get_max_stack_size()

        if moving_slot.itemstack.amount == 0:
            moving_slot.itemstack.clean()
            moving_slot.amount = 0


class InventoryHandler:
    """
    main class for registrating inventories
    """

    def __init__(self):
        self.opened_inventorystack = []
        self.alwaysopened = []
        self.inventorys = []
        self.moving_slot: gui.Slot.Slot = gui.Slot.Slot(allow_player_add_to_free_place=False, allow_player_insert=False,
                                                        allow_player_remove=False)

    def add(self, inventory):
        """
        add an new inventory
        :param inventory: the inventory to add
        """
        if inventory in self.inventorys: return
        self.inventorys.append(inventory)
        if inventory.is_always_open():
            self.alwaysopened.append(inventory)
            self.show(inventory)

    def reload_config(self):
        [inventory.reload_config() for inventory in self.inventorys]

    def show(self, inventory):
        """
        show an inventory
        :param inventory: the inventory to show
        """
        if inventory in self.opened_inventorystack: return
        self.opened_inventorystack.append(inventory)
        inventory.on_activate()

    def hide(self, inventory):
        """
        hide an inventory
        :param inventory: the inventory to hide
        """
        if inventory not in self.opened_inventorystack: return
        if inventory in self.alwaysopened: return
        inventory.on_deactivate()
        self.opened_inventorystack.remove(inventory)

    def remove_one_from_stack(self):
        """
        removes one inventory from stack
        :return: the inventory removed or None if no is active
        """
        stack = self.opened_inventorystack
        stack.reverse()
        for inventory in stack:
            if inventory.is_closable_by_escape():
                self.hide(inventory)
                return inventory

    def close_all_inventorys(self):
        """
        close all inventories
        """
        for inventory in self.opened_inventorystack:
            self.hide(inventory)


G.inventoryhandler = InventoryHandler()

