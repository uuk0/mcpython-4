"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import UIPart, UIPartLable
import re
import pyglet.window.key
import time
import util.opengl
import pyglet

ALL_PATTERN = None
INT_PATTERN = "-0123456789."


class UIPartTextInput(UIPart.UIPart):
    def __init__(self, size, position, anchor_ti="LD", anchor_window="LD", pattern=ALL_PATTERN, default_text="",
                 text_size=10, on_text_update=None, on_enter_press=None, empty_overlay_text=""):
        super().__init__(position, size, anchor_element=anchor_ti, anchor_window=anchor_window)
        self.pattern = pattern
        self.default_text = self.entered_text = default_text
        self.text_size = text_size
        self.selected = False
        self.on_text_update = on_text_update
        self.on_enter_press = on_enter_press
        self.lable = pyglet.text.Label(color=(255, 255, 255, 255), anchor_y='center')
        self.empty_overlay_text = empty_overlay_text

        self.update_lable()

    def update_lable(self):
        x, y = self.get_real_position()
        self.lable.x, self.lable.y = x + 5, y + self.bboxsize[1] // 2
        if not self.selected and self.entered_text == "":
            if self.empty_overlay_text != "":
                self.lable.text = self.empty_overlay_text
                self.lable.color = (150, 150, 150, 255)
                self.lable.font_size = self.bboxsize[1] // 4
        else:
            self.lable.color = (255, 255, 255, 255)
            self.lable.font_size = self.bboxsize[1] // 3
            self.lable.text = self.entered_text + (" " if time.time() // 2 % 2 == 0 or not self.selected else "_")
            while self.lable.content_height > self.bboxsize[0] - 6:
                self.lable.text = self.lable.text[1:]

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.master[0].eventbus.subscribe("user:keyboard:enter", self.on_text)

    def on_draw_2d(self):
        self.update_lable()
        x, y = self.get_real_position()
        sx, sy = self.bboxsize
        util.opengl.draw_rectangle((x, y), (sx, sy))
        util.opengl.draw_line_rectangle((x+2, y+1), (sx-3, sy-3), color=(1., 1., 1.))
        self.lable.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        rx, ry = self.get_real_position()
        sx, sy = self.bboxsize
        if 0 <= x - rx <= sx and 0 <= y - ry <= sy:
            self.selected = True
        else:
            self.selected = False

    def on_key_press(self, key, mod):
        if self.selected:
            if key == pyglet.window.key.ESCAPE:
                self.selected = False
            elif key == pyglet.window.key.ENTER:
                self.selected = False
                if self.on_enter_press:
                    self.on_enter_press()
            elif key == 65288 and len(self.entered_text) > 0:  # BACK
                self.entered_text = self.entered_text[:-1]

    def on_text(self, text: str):
        if self.selected and (self.pattern is None or text in self.pattern):
            self.entered_text += text
            if self.on_text_update:
                self.on_text_update()

    def reset(self): self.entered_text = self.default_text

