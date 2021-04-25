from primitives import GameObject
import pygame
import constants as c

class FadeObject(GameObject):
    def __init__(self, game, x, y):
        self.frames = [game.load_image("young_child.png")]
        self.special_frames = {"Mistake": game.load_image("young_child_mistake.png")}
        self.x = x
        self.y = y
        self.current_frame = 0
        self.age = 0
        self.fps = 2

        self.shadowless = False
        self.make_shadows()
        self.active_special = None
        self.since_special = 999

    def update(self, dt, events):
        self.since_special += dt
        if self.since_special >= 0.05:
            self.active_special = None
        self.age += dt
        self.current_frame = int(self.age*self.fps) % len(self.frames)

    def set_special_frame(self, frame):
        if frame in self.special_frames:
            self.since_special = -1/(self.fps) - (1 - ((self.age*self.fps) % 1))
            self.active_special = frame

    def get_current_frame(self):
        if self.active_special:
            return self.special_frames[self.active_special]
        return self.frames[self.current_frame]

    def get_current_shadow(self):
        if self.shadowless:
            return None
        if self.active_special:
            return self.special_shadows[self.active_special]
        return self.shadows[self.current_frame]

    def make_shadows(self):
        if self.shadowless:
            return
        self.shadows = []
        for item in self.frames:
            shadow = pygame.mask.from_surface(item)
            shadow = shadow.to_surface(setcolor=(0, 0, 0, 40), unsetcolor=(0, 0, 0, 0))
            self.shadows.append(shadow)
        self.special_shadows = {}
        for item in self.special_frames:
            shadow = pygame.mask.from_surface(self.special_frames[item])
            shadow = shadow.to_surface(setcolor=(0, 0, 0, 40), unsetcolor=(0, 0, 0, 0))
            self.special_shadows[item] = shadow


    def draw_shadow(self, surf, x, y):
        if self.shadowless:
            return
        shadow = self.get_current_shadow()
        surf.blit(shadow, (x-8, y+6))

    def draw(self, surf, offset=(0, 0)):
        frame = self.get_current_frame()
        x = self.x - frame.get_width()//2 + offset[0]
        y = self.y - frame.get_height()//2 + offset[1]
        self.draw_shadow(surf, x, y)
        surf.blit(frame, (x, y))

    def draw_align_bottom(self, surf, offset=(0, 0)):
        frame = self.get_current_frame()
        x = self.x - frame.get_width()//2 + offset[0]
        y = self.y - frame.get_height() + offset[1]
        self.draw_shadow(surf, x, y)
        surf.blit(frame, (x, y))

class Child(FadeObject):
    def draw(self, surf, offset=(0, 0)):
        self.draw_align_bottom(surf, offset=offset)

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("young_child.png"),
                       game.load_image("young_child_2.png"),
                       game.load_image("young_child.png", flipped=True),
                       game.load_image("young_child_2.png", flipped=True)]
        self.make_shadows()

class Teen(FadeObject):
    def draw(self, surf, offset=(0, 0)):
        self.draw_align_bottom(surf, offset=offset)

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("teen.png"),
                       game.load_image("teen.png", flipped=True)]
        self.special_frames = {"Mistake": game.load_image("teen_mistake.png")}
        self.make_shadows()


class Bench(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("bench.png")]
        self.make_shadows()

class Piano(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("piano.png")]
        self.make_shadows()

class Walls(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("walls.png")]
        self.shadowless = True

class Mom(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("mom.png"),
                       game.load_image("mom_2.png"),
                       game.load_image("mom.png", flipped=True),
                       game.load_image("mom_2.png", flipped=True)]
        self.make_shadows()

    def draw(self, surf, offset=(0, 0)):
        self.draw_align_bottom(surf, offset=offset)

class MomGray(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("mom_gray.png"),
                       game.load_image("mom_gray_2.png"),
                       game.load_image("mom_gray.png", flipped=True),
                       game.load_image("mom_gray_2.png", flipped=True)]
        self.make_shadows()

    def draw(self, surf, offset=(0, 0)):
        self.draw_align_bottom(surf, offset=offset)

class Background(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("background.png")]
        self.shadowless = True
        self.cloud_1 = (c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT*0.3)
        self.cloud_2 = (c.WINDOW_WIDTH*0.1, c.WINDOW_HEIGHT//5)

        self.cloud_1_surf = game.load_image("cloud_1.png")
        self.cloud_2_surf = game.load_image("cloud_2.png")

    def update(self, dt, events):
        self.cloud_1 = self.cloud_1[0] + dt*20, self.cloud_1[1]
        self.cloud_2 = self.cloud_2[0] + dt*20, self.cloud_2[1]
        if self.cloud_1[0] > c.WINDOW_WIDTH:
            self.cloud_1 = -100, self.cloud_1[1]
        if self.cloud_2[0] > c.WINDOW_WIDTH:
            self.cloud_2 = -100, self.cloud_2[1]

    def draw(self, surf, offset=(0, 0)):
        super().draw(surf, offset)
        surf.blit(self.cloud_1_surf, self.cloud_1)
        surf.blit(self.cloud_2_surf, self.cloud_2)

class Curtains(FadeObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.frames = [game.load_image("curtains.png")]
        self.shadowless = True