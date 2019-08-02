"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import StatePart
import globals as G
from config import FLYING_SPEED, WALKING_SPEED, GRAVITY, TERMINAL_VELOCITY, PLAYER_HEIGHT, JUMP_SPEED
from pyglet.window import key, mouse
import pyglet
import gui.ItemStack


class StatePartGame(StatePart.StatePart):
    mouse_press_time = 0
    block_looking_at = None

    def __init__(self, activate_physics=True, activate_mouse=True, activate_keyboard=True, activate_3d_draw=True,
                 activate_focused_block=True, glcolor3d=(1., 1., 1.), activate_crosshair=True,
                 clearcolor=(0.5, 0.69, 1.0, 1)):
        self.activate_physics = activate_physics
        self.activate_mouse = activate_mouse
        self.activate_keyboard = activate_keyboard
        self.activate_3d_draw = activate_3d_draw
        self.activate_focused_block_draw = activate_focused_block
        self.activate_crosshair = activate_crosshair
        self.glcolor3d = glcolor3d
        self.clearcolor = clearcolor

        self.event_functions = [("gameloop:tick:end", self.on_update),
                                ("user:mouse:press", self.on_mouse_press),
                                ("user:mouse:motion", self.on_mouse_motion),
                                ("user:keyboard:press", self.on_key_press),
                                ("user:keyboard:release", self.on_key_release),
                                ("render:draw:3d", self.on_draw_3d),
                                ("render:draw:2d", self.on_draw_2d)]

    def activate(self):
        for k in G.window.mouse_pressing:
            G.window.mouse_pressing[k] = False
        for eventname, function in self.event_functions:
            G.eventhandler.activate_to_callback(eventname, function)

    def deactivate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.deactivate_from_callback(eventname, function)

    @G.eventhandler("gameloop:tick:end", callactive=False)
    def on_update(self, dt):
        if any(G.window.mouse_pressing.values()):
            self.mouse_press_time += dt

        if self.activate_physics:
            m = 8
            dt = min(dt, 0.2)
            for _ in range(m):
                self._update(dt / m)

        if G.window.exclusive and any(G.window.mouse_pressing.values()):
            vector = G.window.get_sight_vector()
            blockpos, previous = G.window.model.hit_test(G.window.position, vector)
            if blockpos != self.block_looking_at:
                self.block_looking_at = blockpos
                self.mouse_press_time = 0

            if G.window.mouse_pressing[mouse.LEFT] and blockpos in G.model.world:
                block = G.model.world[blockpos]
                item = G.player.get_active_inventory_slot().itemstack
                if G.player.gamemode == 1:
                    if self.mouse_press_time >= 0.10:
                        G.model.remove_block(blockpos)
                elif G.player.gamemode == 0:
                    if self.mouse_press_time >= block.get_brake_time(item):
                        G.player.add_to_free_place(gui.ItemStack.ItemStack(G.model.world[blockpos].get_name()))
                        G.model.remove_block(blockpos)
                # todo: check if brakeable in gamemode 2
            if G.window.mouse_pressing[mouse.RIGHT] and previous:
                slot = G.player.get_active_inventory_slot()
                if slot.itemstack.item and slot.itemstack.item.has_block() and self.mouse_press_time > 0.12:
                    if G.player.gamemode == 1:
                        G.model.add_block(previous, slot.itemstack.item.get_block(), kwargs={"setted_to": blockpos})
                    elif G.player.gamemode == 2:
                        G.model.add_block(previous, slot.itemstack.item.get_block(), kwargs={"setted_to": blockpos})
                        slot.itemstack.amount -= 1
                        if slot.itemstack.amount == 0:
                            slot.itemstack.clean()
                    self.mouse_press_time = 0
                    # todo: check if setable in gamemode 2
            if G.window.mouse_pressing[mouse.MIDDLE] and blockpos and self.mouse_press_time > 0.1:
                self.mouse_press_time = 0
                block = G.window.model.world[blockpos]
                selected_slot = G.player.get_active_inventory_slot()
                for inventoryname, reverse in G.player.inventory_order:
                    inventory = G.player.inventorys[inventoryname]
                    slots: list = inventory.slots
                    if reverse:
                        slots.reverse()
                    for slot in slots:
                        if slot.itemstack.item and slot.itemstack.item.has_block() and \
                                slot.itemstack.item.get_block() == block.get_name():
                            if inventoryname != "hotbar":
                                selected_slot.itemstack, slot.itemstack = slot.itemstack, selected_slot.itemstack
                            else:
                                G.player.set_active_inventory_slot(slots.index(slot))
                            return
                if G.player.gamemode == 1:
                    old_itemstack = selected_slot.itemstack
                    selected_slot.itemstack = gui.ItemStack.ItemStack(block.get_name())
                    G.player.add_to_free_place(old_itemstack)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if G.window.flying else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = G.window.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not G.window.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            G.window.dy -= dt * GRAVITY
            G.window.dy = max(G.window.dy, -TERMINAL_VELOCITY)
            dy += G.window.dy * dt
        # collisions
        x, y, z = G.window.position
        if G.player.gamemode != 3:
            x, y, z = G.window.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        else:
            x, y, z = x + dx, y + dy, z + dz
        G.window.position = (x, y, z)

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    @G.eventhandler("user:mouse:motion", callactive=False)
    def on_mouse_motion(self, x, y, dx, dy):
        if G.window.exclusive and self.activate_mouse:
            m = 0.15
            x, y = G.window.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            G.window.rotation = (x, y)

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if not self.activate_keyboard: return
        if symbol == key.W:
            G.window.strafe[0] -= 1
        elif symbol == key.S:
            G.window.strafe[0] += 1
        elif symbol == key.A:
            G.window.strafe[1] -= 1
        elif symbol == key.D:
            G.window.strafe[1] += 1
        elif symbol == key.SPACE:
            if G.window.dy == 0:
                G.window.dy = JUMP_SPEED
        elif symbol == key.TAB and G.player.gamemode == 1:
            G.window.flying = not G.window.flying
        elif symbol in G.window.num_keys and G.player.gamemode in (0, 1):
            index = symbol - G.window.num_keys[0]
            G.player.set_active_inventory_slot(index)

    @G.eventhandler("user:keyboard:release", callactive=False)
    def on_key_release(self, symbol, modifiers):
        if not self.activate_keyboard: return
        if symbol == key.W:
            G.window.strafe[0] += 1
        elif symbol == key.S:
            G.window.strafe[0] -= 1
        elif symbol == key.A:
            G.window.strafe[1] += 1
        elif symbol == key.D:
            G.window.strafe[1] -= 1

    @G.eventhandler("render:draw:3d", callactive=False)
    def on_draw_3d(self):
        pyglet.gl.glClearColor(*self.clearcolor)
        pyglet.gl.glColor3d(*self.glcolor3d)
        if self.activate_3d_draw:
            G.window.model.batch.draw()
            if self.activate_focused_block_draw and G.player.gamemode != 3:
                G.window.draw_focused_block()

    @G.eventhandler("render:draw:2d", callactive=False)
    def on_draw_2d(self):
        G.window.draw_label()
        if self.activate_crosshair:
            G.window.draw_reticle()

