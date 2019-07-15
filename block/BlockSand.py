"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""
import globals as G
from . import Block
import event.TickHandler


@G.blockhandler
class BlockSand(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:sand"

    def get_tex_coords(self) -> list:
        return [(1, 1)] * 3

    def on_block_update(self):
        x, y, z = self.position
        if (x, y-1, z) not in G.model.world:
            event.TickHandler.handler.bind(self.fall, 10)

    def fall(self):
        x, y, z = self.position
        if (x, y - 1, z) not in G.model.world:
            G.model.remove_block(self)
            G.model.add_block((x, y - 1, z), self)
