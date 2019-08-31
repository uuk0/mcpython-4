import globals as G


class EntityRenderer:
    def __init__(self):
        self.renderentries = []

    def show(self, entity):
        pass

    def hide(self, entity):
        pass

    def add_box(self, position, rotation, size, texture, regions):
        x, y, z = position
        rx, ry, rz = rotation
        sx, sy, sz = size

    def add_side(self, position, rotation, size, texture, regions):
        pass


class Entity:
    renderer: EntityRenderer = None

    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation

    def show(self):
        if self.renderer:
            self.renderer.show(self)

    def hide(self):
        if self.renderer:
            self.renderer.hide(self)

