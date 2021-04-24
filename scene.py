from primitives import GameObject

import time
import constants as c
from note import Note
import pygame


class Scene(GameObject):
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.is_over = False

    def next_scene(self):
        return Scene

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        pass


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tempo = 144  # BPM
        self.song = [[8],[],[5],[],[],[],[6],[],[7],[]]*5
        self.start = time.time() + (c.BEATS_BEFORE_SONG / self.tempo * 60)
        self.last_beat = int(self.current_beat())
        self.notes = []
        self.thresh = 0.3

    def since_start(self):
        return time.time() - self.start

    def current_beat(self):
        return self.since_start() / 60 * self.tempo

    def update(self, dt, events):
        if int(self.current_beat()) > self.last_beat:
            self.last_beat = int(self.current_beat())
            self.on_new_beat()
        for note in self.notes[:]:
            note.update(dt, events)
            note.color = (255, 0, 0)
            if note.destroyed:
                self.notes.remove(note)
        for col in c.NOTES:
            for note in self.notes_near_bar(0.25, col):
                note.color = (255, 255, 0)
        self.update_controls(dt, events)

    def update_controls(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in c.DEFAULT_CONTROLS:
                    col = c.DEFAULT_CONTROLS[event.key]
                    self.fire_column(col)

    def fire_column(self, col):
        for note in self.notes_near_bar(self.thresh, col):
            note.destroy()

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        pygame.draw.line(surface,(255, 255, 255), (0, c.NOTE_TARGET_Y), (c.WINDOW_WIDTH, c.NOTE_TARGET_Y))
        for note in self.notes:
            note.draw(surface, offset=offset)

    def on_new_beat(self):
        self.spawn_notes(self.last_beat + 6)
        pass

    def spawn_notes(self, beat):
        if beat >= len(self.song):
            return
        for line in self.song[beat]:
            note = Note(self.game, line, self, beat)
            self.notes.append(note)

    def notes_in_column(self, col):
        for note in self.notes:
            if note.note_key == col:
                yield note

    def notes_near_bar(self, thresh, col):
        for note in self.notes_in_column(col):
            if note.beat - self.current_beat() > thresh:
                return
            elif note.beat - self.current_beat() < -thresh:
                continue
            yield note