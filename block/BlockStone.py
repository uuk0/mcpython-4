"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
from . import Block


@G.blockhandler
class BlockStone(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stone"

    def get_model_name(self):
        return "block/stone"

