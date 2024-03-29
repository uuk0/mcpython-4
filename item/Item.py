"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import PIL.Image


class Item:
    @classmethod
    def get_used_texture_files(cls):
        return [cls.get_default_item_image_location()]

    @staticmethod
    def get_name() -> str:
        return "minecraft:unknown_item"

    @staticmethod
    def has_block() -> bool:
        return True

    def get_block(self) -> str:
        return self.get_name()

    @staticmethod
    def get_default_item_image_location() -> str:
        raise NotImplementedError()

    def get_active_image_location(self):
        return self.get_default_item_image_location()

    def __init__(self):
        pass

    def get_max_stack_size(self) -> int:
        return 64

    def __eq__(self, other):
        if not issubclass(type(other), Item): return False
        return other.get_name() == self.get_name()

    def on_player_interact(self, block, button, modifiers) -> bool:
        return False

