import sys

import pygame
import random
import time

import constants as c
from scene import Scene, LevelScene, Title, Logo


class Game:
    def __init__(self):
        pygame.init()

        if not c.FULLSCREEN:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        else:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE, pygame.FULLSCREEN)

        pygame.display.set_caption(c.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.image_dict = {}

        self.lost_most_recent = False

        self.load_sounds()
        self.last_music_play = time.time()
        self.current_scene = Logo(self)
        self.main()

    def load_sounds(self):
        self.sample_music = pygame.mixer.Sound(c.sound_path("sample_music.ogg"))
        self.sample_music.set_volume(0.1)
        self.song_1 = pygame.mixer.Sound(c.sound_path("song_1.ogg"))
        self.song_1.set_volume(0.1)
        self.song_2 = pygame.mixer.Sound(c.sound_path("song_2.ogg"))
        self.song_2.set_volume(0.1)
        self.song_3 = pygame.mixer.Sound(c.sound_path("song_3.ogg"))
        self.song_3.set_volume(0.10)
        self.song_5 = pygame.mixer.Sound(c.sound_path("song_5.ogg"))
        self.song_5.set_volume(0.10)

        self.take_damage = pygame.mixer.Sound(c.sound_path("take_damage.wav"))
        self.take_damage.set_volume(0.2)
        self.mom_talk = pygame.mixer.Sound(c.sound_path("mom_talk_long.wav"))
        self.mom_talk.set_volume(0.2)
        self.rain = pygame.mixer.Sound(c.sound_path("rain.wav"))
        self.rain.set_volume(0.01)

        self.fade = pygame.mixer.Sound(c.sound_path("fade.ogg"))
        self.fade.set_volume(0.1)

    def load_image(self, path, flipped=False):
        if path not in self.image_dict:
            self.image_dict[path] = pygame.image.load(c.image_path(path))
        if flipped:
            return pygame.transform.flip(self.image_dict[path], True, False)
        return self.image_dict[path]

    def update_global(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        dt = self.clock.tick(c.FPS)/1000

        return dt, events

    def main(self):
        lag = 0
        while True:
            dt, events = self.update_global()
            lag += dt
            times = 0
            while lag > 1/c.SIM_FPS:
                times += 1
                lag -= 1/c.SIM_FPS
                self.current_scene.update(1/c.SIM_FPS, events)
                events = []
                if times > 3:
                    lag = 0
                    break
            self.current_scene.draw(self.screen, (0, 0))
            if self.current_scene.is_over:
                old_scene = self.current_scene
                self.current_scene = None
                self.current_scene = old_scene.next_scene()
            pygame.display.flip()


if __name__ == '__main__':
    Game()