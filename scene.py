from primitives import GameObject

import time
import constants as c
from note import Note
import pygame
from objects import *
from particle import *
import math


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
        self.level = 1
        self.subdivision = 4
        self.tempo = 120 * self.subdivision  # BPM
        self.song = c.SONG_1#[1], [2], [3], [4], [8],[],[5],[],[],[],[],[],[6],[],[7],[],[],[],[],[]]*5
        self.start = time.time() + (0 / self.tempo * 60)
        self.game.song_1.play()
        self.last_beat = int(self.current_beat())
        self.notes = []
        self.thresh = 0.3 * self.subdivision
        self.player = Child(game, *c.RIGHT_POS)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS),
                        Mom(game, *c.LEFT_POS),
                        self.player]

        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)

        self.heart = game.load_image("heart.png")

        self.particles = []
        self.active_notes = {5, 6, 7, 8}

        self.since_last_shake = 999
        self.shake_amp = 0

    def shake(self, amp = 10):
        if amp > self.shake_amp:
            self.since_last_shake = 0
            self.shake_amp = amp

    def since_start(self):
        return time.time() - self.start

    def current_beat(self):
        return self.since_start() / 60 * self.tempo

    def sinsq(self):
        t = self.current_beat() * math.pi / self.subdivision
        sint = math.sin(t)
        return c.sign(sint) * abs(sint)**0.25

    def draw_heart(self, surface, offset=(0, 0)):
        t = self.current_beat() * math.pi / 2 / self.subdivision
        sint = math.cos(t - 0.3)
        scale = 0.7 + 0.3 * abs(sint)**9
        width = int(self.heart.get_width() * scale)
        heart = pygame.transform.scale(self.heart, (width, width))
        x = c.WINDOW_WIDTH//2 - heart.get_width()//2 + offset[0]
        y = c.NOTE_TARGET_Y - heart.get_height()//2 + offset[1]
        surface.blit(heart, (x, y))

    def update(self, dt, events):
        self.since_last_shake += dt
        self.shake_amp *= 0.008**dt
        self.shake_amp = max(0, self.shake_amp - 10*dt)

        if int(self.current_beat()) > self.last_beat:
            self.last_beat = int(self.current_beat())
            self.on_new_beat()
        for note in self.notes[:]:
            note.update(dt, events)
            if note.destroyed:
                self.notes.remove(note)
                self.make_note_splash(note)
        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.dead:
                self.particles.remove(particle)
        for col in c.NOTES:
            for _ in self.notes_near_bar(0.25, col):
                pass
        for object in self.objects:
            object.update(dt, events)
        self.update_controls(dt, events)

    def update_controls(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in c.DEFAULT_CONTROLS:
                    col = c.DEFAULT_CONTROLS[event.key]
                    self.fire_column(col)

    def make_note_splash(self, note):
        if note.missed:
            return
        for i in range(14):
            self.particles.append(NoteParticle(self.game, note))
        self.particles.append(NoteExplosion(self.game, note))
        self.shake(4)

    def fire_column(self, col):
        for note in self.notes_near_bar(self.thresh, col):
            note.destroy()
            return
        for note in self.notes_within_missing_distance(col):
            if not note.missed:
                note.miss()
                self.miss_note_effect()
                return

    def draw_bar(self, surface, offset=(0, 0)):
        pygame.draw.line(surface, (255, 255, 255), (0, c.NOTE_TARGET_Y), (c.WINDOW_WIDTH, c.NOTE_TARGET_Y))
        sinsq = self.sinsq()
        for note in c.NOTES:
            newnote = note
            if note >= 5:
                newnote = 9 - note
            x = c.TARGET_MARGIN + (newnote - 1) * c.TARGET_SPACING
            if note >= 5:
                x = c.WINDOW_WIDTH - x
            if note in self.active_notes:
                pygame.draw.circle(surface, (255, 255, 255), (x, c.NOTE_TARGET_Y), 15 + int(sinsq*3), 2)
            else:
                pygame.draw.circle(surface, (255, 255, 255), (x, c.NOTE_TARGET_Y), 4)
            sinsq *= -1

    def draw(self, surface, offset=(0, 0)):
        xoff = math.cos(self.since_last_shake * 24) * self.shake_amp
        yoff = math.cos(self.since_last_shake * 19.5) * self.shake_amp
        offset = (offset[0] + xoff, offset[1] + yoff)
        #surface.fill((0, 0, 0))
        new_offset = offset
        for object in self.objects:
            new_offset = new_offset[0] * 1.2, new_offset[1] * 1.2
            object.draw(surface, offset=new_offset)
        self.draw_bar(surface, offset=offset)
        for particle in self.particles:
            particle.draw(surface, offset=offset)
        for note in self.notes:
            note.draw(surface, offset=offset)
        self.draw_heart(surface, offset=offset)

    def on_new_beat(self):
        self.spawn_notes(self.last_beat + 10*self.subdivision)
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
                if not note.missed:
                    note.miss()
                    self.miss_note_effect()
                continue
            yield note

    def miss_note_effect(self):
        self.player.set_special_frame("Mistake")

    def lose(self):
        self.miss_all()

    def miss_all(self):
        for note in self.notes:
            note.miss()

    def notes_within_missing_distance(self, col):
        for note in self.notes_near_bar(2.5, col):
            yield note