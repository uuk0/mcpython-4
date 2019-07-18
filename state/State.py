"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G


class State:
    @staticmethod
    def get_name():
        return "minecraft:unknownstate"

    @staticmethod
    def is_mouse_exclusive():
        return False

    def __init__(self):
        self.parts = self.get_parts()
        G.statehandler.add_state(self)

    def get_parts(self) -> list:
        return []

    def get_event_functions(self) -> list:
        return []

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass
