"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G
from pyglet.window import key
import pyglet
import os
import texture.helpers
import item.Item
import event.TickHandler
import PIL.Image, PIL.ImageDraw

os.makedirs(G.local+"/tmp/generated_items")


class StateBlockItemGenerator(State.State):
    @staticmethod
    def get_name():
        return "minecraft:blockitemgenerator"

    def __init__(self):
        State.State.__init__(self)
        self.blockindex = 0

    def get_parts(self) -> list:
        return [StatePartGame.StatePartGame(activate_physics=False, activate_mouse=False, activate_keyboard=False,
                                            activate_focused_block=False, clearcolor=(1., 1., 1., 0.),
                                            glcolor3d=(1., 1., 1.), activate_crosshair=False)]

    def get_event_functions(self) -> list:
        return []

    def on_activate(self, old):
        G.window.position = (1.5, 2, 1.5)
        G.window.rotation = (-45, -45)
        G.world.get_active_dimension().add_block(
            (0, 0, 0), G.blockhandler.blockclasses[0].get_name(), block_update=False)
        self.blockindex = 0
        event.TickHandler.handler.bind(self.take_image, 5)
        event.TickHandler.handler.bind(self.add_new_screen, 15)

    def on_deactivate(self, new):
        G.world.cleanup()

    def add_new_screen(self):
        self.blockindex += 1
        if self.blockindex >= len(G.blockhandler.blockclasses):
            G.statehandler.switch_to("minecraft:startmenu")
            G.window.position = (0, 10, 0)
            G.window.rotation = (0, 0)
            G.world.get_active_dimension().remove_block((0, 0, 0))
            return
        # print(G.blockhandler.blockclasses[self.blockindex].get_name())
        G.world.get_active_dimension().hide_block((0, 0, 0))
        G.world.get_active_dimension().add_block(
            (0, 0, 0), G.blockhandler.blockclasses[self.blockindex].get_name(), block_update=False)
        # todo: add states
        event.TickHandler.handler.bind(self.take_image, 5)
        event.TickHandler.handler.bind(self.add_new_screen, 15)
        G.world.get_active_dimension().get_chunk(0, 0, generate=False).is_ready = True

    def take_image(self, *args):
        if self.blockindex >= len(G.blockhandler.blockclasses): return
        blockname = G.blockhandler.blockclasses[self.blockindex].get_name()
        file = G.local + "/tmp/generated_items/{}.png".format("_".join(blockname.split(":")))
        pyglet.image.get_buffer_manager().get_color_buffer().save(file)
        image: PIL.Image.Image = texture.helpers.load_image(file)
        part = texture.helpers.get_image_part(image, (240, 129, 558, 447))
        part.save(file)

        @G.itemhandler
        class GeneratedItem(item.Item.Item):
            @staticmethod
            def get_name() -> str:
                return blockname

            @staticmethod
            def get_item_image_location() -> str:
                return file


blockitemgenerator = StateBlockItemGenerator()
