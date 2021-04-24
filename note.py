from primitives import GameObject
import constants as c
import pygame


class Note(GameObject):
    def __init__(self, game, note_key, scene, beat):
        self.scene = scene
        self.beat = beat
        self.note_key = note_key
        self.y = self.get_y()
        self.x = self.get_x()
        self.color = (255, 0, 0)
        self.destroyed = False

    def destroy(self):
        self.destroyed = True

    def get_y(self):
        self.y = (self.beat - self.scene.current_beat())*c.BEAT_HEIGHT + c.NOTE_TARGET_Y
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
        pass

    def draw(self, surf, offset=(0, 0)):
        x = self.x + offset[0]
        y = self.get_y() + offset[1]
        pygame.draw.circle(surf, self.color, (x, y), 15)
        pass