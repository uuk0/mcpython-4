"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.IBlock
import event.TickHandler
import event.TickHandler


@G.registry
class IFallingBlock(block.IBlock.IBlock):
    """
    base injection class for falling block
    """

    @staticmethod
    def get_extension_name() -> str:
        return "falling_block"

    @classmethod
    def get_functions_to_inject(cls) -> dict:
        return {block.IBlock.InjectionMode.IF_NO_OTHER: [cls.get_functions_to_inject, cls.get_extension_name],
                block.IBlock.InjectionMode.PARALLEL: [cls.on_block_update, cls.fall, cls.on_create]}

    @classmethod
    def on_create(cls, self):
        self.fall_cooldown = event.TickHandler.handler.active_tick - 10

    @classmethod
    def on_block_update(cls, self):
        x, y, z = self.position
        block = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not block and event.TickHandler.handler.active_tick - self.fall_cooldown >= 10:
            self.fall_cooldown = event.TickHandler.handler.active_tick
            event.TickHandler.handler.bind(cls.fall, 10, args=[self])

    @classmethod
    def fall(cls, self, check=True):
        """
        let the block fall
        :param check: weither to check if the block can fall to that position or not
        """
        x, y, z = self.position
        if not check or not G.world.get_active_dimension().get_block((x, y - 1, z)):
            G.world.get_active_dimension().remove_block(self.position, block_update=False)
            G.world.get_active_dimension().add_block((x, y - 1, z), self, block_update=False)
            self.on_block_update()

