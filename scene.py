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
        self.song = c.SONG_1
        self.start = time.time() + (0 / self.tempo * 60)
        self.song_audio = game.song_1
        self.song_audio.play()
        self.last_beat = int(self.current_beat())
        self.thresh = 0.3 * self.subdivision
        self.player = Child(game, *c.RIGHT_POS)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS),
                        Mom(game, *c.LEFT_POS),
                        self.player]

        self.notes = []
        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)

        self.heart = game.load_image("heart.png")

        self.particles = []
        self.active_notes = {5, 6, 7, 8}

        self.since_last_shake = 999
        self.shake_amp = 0

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill((255, 255, 255))
        self.shade_lightness = 255
        self.shade_target_lightness = 0
        self.active_message = None

        self.dialogue_back = pygame.Surface((c.WINDOW_WIDTH, c.DIALOGUE_THICKNESS))
        self.dialogue_back.fill((0, 0, 0))
        self.dialogue_back.set_alpha(0)
        self.dialogue_back_target_alpha = 0
        self.dialogue_back_alpha = 0

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

        if self.shade_target_lightness > self.shade_lightness:
            self.shade_lightness += 1200 * dt
            self.shade_lightness = min(255, self.shade_lightness)
        elif self.shade_target_lightness < self.shade_lightness:
            self.shade_lightness -= 150 * dt
            self.shade_lightness = max(0, self.shade_lightness)

        if self.dialogue_back_target_alpha > self.dialogue_back_alpha:
            self.dialogue_back_alpha += 300 * dt
            self.dialogue_back_alpha = min(self.dialogue_back_target_alpha, self.dialogue_back_alpha)
        elif self.dialogue_back_target_alpha < self.dialogue_back_alpha:
            self.dialogue_back_alpha -= 300 * dt
            self.dialogue_back_alpha = max(self.dialogue_back_target_alpha, self.dialogue_back_alpha)

        if len(self.song) and self.current_beat() > len(self.song):
            self.shade_target_lightness = 255
            if self.shade_lightness >= 255:
                self.end_scene()

    def end_scene(self):
        self.is_over = True
        self.start_next_song()

    def start_next_song(self):
        self.game.last_music_play = time.time()
        self.game.song_2.play()

    def next_scene(self):
        return Level2(self.game)

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
            if not note.missed:
                note.destroy()
            return
        for note in self.notes_within_missing_distance(col):
            if not note.missed:
                note.miss()
                self.miss_note_effect()
            if note.beat - self.current_beat() > 0:
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

        self.dialogue_back.set_alpha(self.dialogue_back_alpha)
        if self.dialogue_back_alpha > 0:
            surface.blit(self.dialogue_back, (0, offset[1] + c.DIALOGUE_HEIGHT - c.DIALOGUE_THICKNESS//2))
            self.active_message.set_colorkey(self.active_message.get_at((0, 0)))
            self.active_message.set_alpha(int(self.dialogue_back_alpha * 3))
            surface.blit(self.active_message,
                         (c.WINDOW_WIDTH//2 - self.active_message.get_width()//2,
                          c.DIALOGUE_HEIGHT - self.active_message.get_height()//2))

        col = int(self.shade_lightness)
        if col > 0:
            self.shade.fill((col, col, col))
            surface.blit(self.shade, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_new_beat(self):
        self.spawn_notes(self.last_beat + 10*self.subdivision)
        print(self.last_beat)

        if self.last_beat == 306 and self.song == c.SONG_1:
            self.miss_all()

        if self.last_beat == 154 and self.song == c.SONG_1:
            self.show_mom_message("so_good.png")

        if self.last_beat == 184 and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 312 and self.song == c.SONG_1:
            self.show_mom_message("hard_part.png")

        if self.last_beat == 340 and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 20 and self.song == c.SONG_2:
            self.show_mom_message("just_how_we_practiced.png")

        if self.last_beat == 50 and self.song == c.SONG_2:
            self.hide_mom_message()

        if self.last_beat == 298 and self.song == c.SONG_2:
            self.show_mom_message("hard_work.png")

        if self.last_beat == 340 and self.song == c.SONG_2:
            self.hide_mom_message()

        pass

    def show_mom_message(self, path):
        self.active_message = self.game.load_image(path)
        self.dialogue_back_target_alpha = 150

    def hide_mom_message(self):
        self.dialogue_back_target_alpha = 0

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
        self.song_audio.fadeout(400)
        self.miss_all()

    def miss_all(self):
        for note in self.notes:
            note.miss()

    def notes_within_missing_distance(self, col):
        for note in self.notes_near_bar(1.5 * self.subdivision, col):
            yield note


class Level2(LevelScene):
    def __init__(self, game):
        super().__init__(game)
        self.level = 2
        self.player = Teen(game, *c.RIGHT_POS)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS),
                        MomGray(game, *c.LEFT_POS),
                        self.player]
        self.song = c.SONG_2
        self.notes = []
        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)
        self.start = self.game.last_music_play
        self.song_audio = self.game.song_2
        self.game.song_1.fadeout(1)