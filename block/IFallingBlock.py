"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.Block
import event.TickHandler
import event.TickHandler


class IFallingBlock(block.Block.Block):
    """
    base injection class for falling block
    """

    def on_create(self):
        self.fall_cooldown = event.TickHandler.handler.active_tick - 10

    def on_block_update(self):
        x, y, z = self.position
        blockinst = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not blockinst and event.TickHandler.handler.active_tick - self.fall_cooldown >= 10:
            self.fall_cooldown = event.TickHandler.handler.active_tick
            event.TickHandler.handler.bind(self.fall, 10, args=[self])

    def fall(self, check=True):
        """
        let the block fall
        :param check: weither to check if the block can fall to that position or not
        """
        x, y, z = self.position
        if not check or not G.world.get_active_dimension().get_block((x, y - 1, z)):
            G.world.get_active_dimension().remove_block(self.position, blockupdateself=False)
            chunk = G.world.get_active_dimension().get_chunk_for_position(self.position)
            chunk.on_block_updated(self.position)
            if y == 0: return
            G.world.get_active_dimension().add_block((x, y - 1, z), self, blockupdateself=False)
            self.on_block_update()

