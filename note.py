from primitives import GameObject
import constants as c
import pygame
import random


class Note(GameObject):
    def __init__(self, game, note_key, scene, beat):
        super().__init__(game)
        self.scene = scene
        self.beat = beat
        self.note_key = note_key
        self.y = self.get_y()
        self.x = self.get_x()
        self.color = c.NOTE_COLORS[note_key]
        self.destroyed = False
        self.radius = 15
        self.path = random.choice(["", "_2", "_3","_4"])
        self.sprite = game.load_image(f"note{self.path}.png").convert()
        self.flair = game.load_image("note_flair.png")
        #self.color_sprite()
        self.color_flair()
        self.sprite.set_colorkey(self.sprite.get_at((0, 0)))
        self.missed = False

    def color_flair(self):
        self.flair = self.flair.copy()
        for x in range(self.flair.get_width()):
            for y in range(self.flair.get_height()):
                r, g, b, a = self.flair.get_at((x, y))
                r, g, b = self.color
                self.flair.set_at((x, y), (r, g, b, a))

    def color_sprite(self):
        self.sprite = self.game.load_image(f"note{self.path}.png").convert()
        surf = self.sprite.copy()
        surf.fill(self.color)
        self.sprite.blit(surf, (0, 0), special_flags=pygame.BLEND_MULT)
        self.sprite.set_colorkey(self.sprite.get_at((0, 0)))

    def destroy(self):
        self.destroyed = True

    def get_y(self):
        self.y = (self.beat - self.scene.current_beat())*c.BEAT_HEIGHT/self.scene.subdivision + c.NOTE_TARGET_Y
        return self.y

    def get_x(self):
        newline = self.note_key
        if self.note_key >= 5:
            newline = 9 - self.note_key
        x = c.TARGET_MARGIN + (newline - 1) * c.TARGET_SPACING
        if self.note_key >= 5:
            x = c.WINDOW_WIDTH - x
        self.x = x
        return x

    def update(self, dt, events):
        if self.missed and self.y < -100:
            self.destroy()
        pass

    def draw(self, surf, offset=(0, 0)):
        x = self.x + offset[0]
        y = self.get_y() + offset[1]
        if not self.missed:
            surf.blit(self.flair, (x - self.flair.get_width()//2, y - self.flair.get_height()//2))
        #pygame.draw.circle(surf, self.color, (x, y), self.radius)
        #pygame.draw.circle(surf, (0, 0, 0), (x, y), self.radius, 1)
        surf.blit(self.sprite, (x - self.sprite.get_width()//2, y - self.sprite.get_height()//2))
        pass

    def miss(self):
        if self.missed:
            return
        self.scene.shake(15)
        self.color = (200, 50, 50)
        self.color_sprite()
        self.missed = True