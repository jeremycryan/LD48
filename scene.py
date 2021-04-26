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
        self.goodness = 1.0

        self.level = 1
        self.subdivision = 4
        self.tempo = 120 * self.subdivision  # BPM
        self.song = c.SONG_1
        self.start = time.time() + (0 / self.tempo * 60)
        self.song_audio = game.song_1
        if hasattr(self, "dontplay"):
            pass
        else:
            self.song_audio.play()
        self.last_beat = int(self.current_beat())
        self.thresh = 0.33 * self.subdivision
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
        self.shade_lightness = 255 if not self.game.lost_most_recent else 0
        self.shade_target_lightness = 0
        self.active_message = None

        self.dialogue_back = pygame.Surface((c.WINDOW_WIDTH, c.DIALOGUE_THICKNESS))
        self.dialogue_back.fill((0, 0, 0))
        self.dialogue_back.set_alpha(0)
        self.dialogue_back_target_alpha = 0
        self.dialogue_back_alpha = 0

        self.lost = False
        self.lose_time = None
        self.shown_lose_message = False
        self.game.lost_most_recent = False

        self.notes_hit = 0

        self.flair = self.game.load_image("flair.png")
        # self.flair = self.processed_flair((255, 0, 0))

    def draw_flair(self, surf, offset=(0, 0)):
        return
        surf.blit(self.flair, (0, 0), special_flags=pygame.BLEND_ADD)

    def processed_flair(self, color):
        new = pygame.Surface((self.flair.get_width(), self.flair.get_height()))
        new.fill(color)
        copy = self.flair.copy()
        copy.blit(new, (0, 0), special_flags=pygame.BLEND_MULT)
        return copy


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
        if self.lost:
            return
        t = self.current_beat() * math.pi / 2 / self.subdivision
        sint = math.cos(t - 0.3)
        scale = (1 + 0.35 * abs(sint)**9) * min(max(self.goodness, 0.01), 1)
        width = int(self.heart.get_width() * scale)
        heart = pygame.transform.scale(self.processed_heart(), (width, width))
        x = c.WINDOW_WIDTH//2 - heart.get_width()//2 + offset[0]
        y = c.NOTE_TARGET_Y - heart.get_height()//2 + offset[1]
        surface.blit(heart, (x, y))

    def processed_heart(self):
        darkness = max(min(int(((self.goodness*1.2)) * 255), 255), 50)
        surf = self.heart.copy()
        surf.fill((0, 0, 0))
        surf.set_alpha((255 - darkness))
        copy = self.heart.convert()
        copy.blit(surf, (0, 0))
        copy.set_colorkey((0, 0, 0))
        return copy

    def update(self, dt, events):
        self.since_last_shake += dt
        self.shake_amp *= 0.008**dt
        self.shake_amp = max(0, self.shake_amp - 10*dt)

        if self.goodness <= 0 and not self.lost:
            self.lose()
        self.goodness += c.GOODNESS_PER_SECOND*dt
        if self.goodness > 1:
            self.goodness = 1
        if self.song == c.SONG_1:
            self.goodness = max(0.1, self.goodness)

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
            for _ in self.notes_near_bar(self.thresh, col):
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

        if len(self.song) and self.current_beat() > len(self.song) and not self.lost:
            if self.shade_target_lightness != 255:
                self.shade_target_lightness = 255
                if not self.lost:
                    self.start_next_song()
                else:
                    if self.song_audio:
                        self.song_audio.play()
                    self.game.last_music_play = time.time()
            if self.shade_lightness >= 255:
                self.end_scene()

        # for event in events:
        #     if event.type==pygame.KEYDOWN:
        #         if event.key == pygame.K_SPACE:
        #             self.end_scene()
        #             self.start_next_song()
        #         if event.key == pygame.K_l:
        #             self.lose()

    def end_scene(self):
        self.is_over = True

    def start_next_song(self):
        self.game.last_music_play = time.time()
        self.game.song_2.play()

    def next_scene(self):
        if self.lost:
            return LevelScene(self.game)
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
                self.goodness += c.GOODNESS_PER_NOTE
                self.notes_hit += 1
                return
        if len(list(self.notes_near_bar(self.thresh, col))):
            return
        for note in self.notes_within_missing_distance(col):
            if not note.missed:
                note.miss()
                self.goodness -= c.GOODNESS_PER_MISSED_NOTE
                self.game.take_damage.play()
                self.miss_note_effect()
            if note.beat - self.current_beat() > -self.thresh:
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
        self.draw_flair(surface, offset=offset)
        self.draw_bar(surface, offset=offset)
        for particle in self.particles:
            particle.draw(surface, offset=offset)
        for note in self.notes:
            note.draw(surface, offset=offset)
        self.draw_heart(surface, offset=offset)

        self.dialogue_back.set_alpha(self.dialogue_back_alpha)
        if self.dialogue_back_alpha > 0:
            yscale = self.dialogue_back_alpha/150 * 0.4 + 0.6
            copy = pygame.transform.scale(self.dialogue_back, (c.WINDOW_WIDTH, int(self.dialogue_back.get_height() * yscale)))
            yoff = (1 - yscale)/2 * self.dialogue_back.get_height()
            surface.blit(copy, (0, offset[1] + yoff + c.DIALOGUE_HEIGHT - c.DIALOGUE_THICKNESS//2))
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
        #print(self.last_beat)

        s1off = 14*4*self.subdivision

        if self.lost and not self.shown_lose_message:
            self.lose_time = time.time()
            self.shown_lose_message = True
            if not self.song == c.SONG_5:
                self.show_mom_message("can_do_better.png")
            else:
                self.show_mom_message("better_than_that.png")
            self.song = []

        if self.lost and self.shown_lose_message and time.time() - self.lose_time > 4:
            self.hide_mom_message()

        if self.lost and time.time() - self.lose_time > 4.5:
            self.shade_target_lightness = 255

        if self.lost and time.time() - self.lose_time > 5:
            self.end_scene()
            if self.song_audio and hasattr(self, "dontplay"):
                self.song_audio.play()
            self.game.last_music_play = time.time()

        if self.lost:
            return


        if self.last_beat == 20 and self.song == c.SONG_1:
            self.show_mom_message("your_age.png")

        if self.last_beat == 50 and self.song == c.SONG_1:
            self.show_mom_message("sparkle.png")

        if self.last_beat == 80 and self.song == c.SONG_1:
            self.show_mom_message("high_notes.png")

        if self.last_beat == 110 and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 190 and self.song == c.SONG_1 and not self.notes_hit >= 4:
            self.lose(override=True)

        if self.last_beat == 200 and self.song == c.SONG_1:
            self.show_mom_message("here_we_go.png")

        if self.last_beat == 235 and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 306 + s1off and self.song == c.SONG_1:
            self.miss_all()

        if self.last_beat == 154 + s1off and self.song == c.SONG_1:
            self.show_mom_message("so_good.png")

        if self.last_beat == 184 + s1off and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 312 + s1off and self.song == c.SONG_1:
            self.show_mom_message("hard_part.png")

        if self.last_beat == 340 + s1off and self.song == c.SONG_1:
            self.hide_mom_message()

        if self.last_beat == 20 and self.song == c.SONG_2:
            self.show_mom_message("just_how_we_practiced.png")

        if self.last_beat == 50 and self.song == c.SONG_2:
            self.hide_mom_message()

        if self.last_beat == 286 and self.song == c.SONG_2:
            self.show_mom_message("hard_work.png")

        if self.last_beat == 310 and self.song == c.SONG_2:
            self.hide_mom_message()

        if self.last_beat == 200 and self.song == c.SONG_3:
            self.show_mom_message("bitter_older.png")

        if self.last_beat == 235 and self.song == c.SONG_3:
            self.show_mom_message("no_wonder.png")

        if self.last_beat == 270 and self.song == c.SONG_3:
            self.show_mom_message("fingers_play.png")

        if self.last_beat == 315 and self.song == c.SONG_3:
            self.hide_mom_message()

        s5extra = 4*4*self.subdivision

        if self.last_beat == 0 + s5extra and self.song == c.SONG_5:
            self.show_mom_message("grandmas_favorite.png")

        if self.last_beat == 40 + s5extra and self.song == c.SONG_5:
            self.hide_mom_message()

        if self.last_beat == 380 + s5extra and self.song == c.SONG_5:
            self.show_mom_message("a_bit_tricky.png")
            self.active_notes = {1, 2, 3, 4, 5, 6, 7, 8}

        if self.last_beat == 415 + s5extra and self.song == c.SONG_5:
            self.hide_mom_message()

        pass

    def show_mom_message(self, path):
        self.active_message = self.game.load_image(path)
        self.dialogue_back_target_alpha = 150
        self.game.mom_talk.play()

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
                    self.goodness -= c.GOODNESS_PER_MISSED_NOTE
                    self.game.take_damage.play()
                    self.miss_note_effect()
                continue
            yield note

    def miss_note_effect(self):
        self.player.set_special_frame("Mistake")

    def lose(self, override=False):
        if self.song == c.SONG_1 and not override:
            return
        if self.song_audio:
            self.song_audio.fadeout(800)
        self.miss_all()
        self.lost = True
        self.lose_time = time.time()
        #self.game.lost_most_recent = True

    def miss_all(self):
        self.miss_note_effect()
        for note in self.notes:
            note.miss()
        self.goodness = 0

    def notes_within_missing_distance(self, col):
        for note in self.notes_near_bar(0.8 * self.subdivision, col):
            yield note


class Level2(LevelScene):
    def __init__(self, game):
        self.dontplay = True
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
        self.game.song_1.fadeout(100)

    def start_next_song(self):
        self.game.last_music_play = time.time()
        self.game.song_3.play()

    def next_scene(self):
        if self.lost:
            return Level2(self.game)
        return Level3(self.game)


class Level3(LevelScene):
    def __init__(self, game):
        self.dontplay = True
        super().__init__(game)
        self.level = 3
        self.player = Adult(game, *c.CENTER_POS)
        self.objects = [BackgroundEvening(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        WallsEvening(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Granny(game, *c.GRANNY_POS),
                        Bench(game, *c.BENCH_POS),
                        self.player]
        self.song = c.SONG_3
        self.notes = []
        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)
        self.start = self.game.last_music_play
        self.song_audio = self.game.song_3
        self.game.song_2.fadeout(100)
        self.game.song_1.fadeout(100)
        self.active_notes = {1, 2, 3, 4, 5, 6, 7, 8}

    def next_scene(self):
        if self.lost:
            return Level3(self.game)
        return Level4(self.game)

    def start_next_song(self):
        self.game.last_music_play = time.time()
        #self.game.song_3.play()


class Level4(LevelScene):
    def __init__(self, game):
        self.dontplay = True
        super().__init__(game)
        self.level = 4
        self.player = Adult(game, *c.CENTER_POS)
        self.objects = [BackgroundNight(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        WallsNight(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS)]
        self.song = c.SONG_4
        self.notes = []
        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)
        self.start = self.game.last_music_play
        self.song_audio = None
        self.game.song_3.fadeout(1)
        self.game.song_2.fadeout(1)
        self.game.song_1.fadeout(1)
        self.active_notes = set()
        self.game.rain.play()
        self.since_rain = 0

    def draw_heart(self, surface, offset=(0, 0)):
        pass

    def next_scene(self):
        self.game.rain.fadeout(1000)
        if self.lost:
            return Level4(self.game)
        return Level5(self.game)

    def start_next_song(self):
        self.game.last_music_play = time.time()
        self.game.song_5.play()

    def update(self, dt, events):
        super().update(dt, events)
        self.since_rain += dt
        if self.since_rain > 3.5:
            self.game.rain.play()
            self.since_rain = 0


class Level5(LevelScene):
    def __init__(self, game):
        self.dontplay = True
        super().__init__(game)
        self.level = 4
        self.player = Adult(game, *c.LEFT_POS)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        PianoFinale(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS),
                        self.player,
                        Daughter(game, *c.RIGHT_POS)]
        self.song = c.SONG_5
        self.notes = []
        for i in range(self.last_beat + 10*self.subdivision + 1):
            self.spawn_notes(i)
        self.start = self.game.last_music_play
        self.song_audio = game.song_5
        self.active_notes = {1, 2, 3, 4}

    def next_scene(self):
        if self.lost:
            return Level5(self.game)
        return Delay(self.game)

    def start_next_song(self):
        self.game.last_music_play = time.time()
        #self.game.song_4.play()


class Title(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS)]
        self.enter_pressed = False
        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((0, 0, 0))
        self.ftarget = 0
        self.falpha = 255
        self.age = 0
        self.enter = self.game.load_image("press_enter.png")


    def update(self, dt, events):
        self.age += dt
        super().update(dt, events)
        for item in self.objects:
            item.update(dt, events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.enter_pressed:
                        self.enter_pressed = True
                        self.game.fade.play()
                        self.flare.fill((255, 255, 255))
                        self.ftarget = 255

        if self.falpha < self.ftarget:
            self.falpha += 1000 * dt
            self.falpha = min(self.ftarget, self.falpha)
            if self.falpha == 255:
                self.is_over = True
        if self.falpha > self.ftarget:
            self.falpha -= 400 * dt
            self.falpha = max(self.ftarget, self.falpha)

    def next_scene(self):
        return Instructions(self.game)

    def draw(self, surface, offset=(0, 0)):
        for item in self.objects:
            item.draw(surface, offset=offset)

        if self.age % 1 < 0.5:
            x = c.WINDOW_WIDTH//2 - self.enter.get_width()//2
            y = c.WINDOW_HEIGHT - self.enter.get_height() - 10
            surface.blit(self.enter, (x, y))

        if self.falpha > 0 and self.ftarget == 255:
            a = int(self.falpha)
            self.flare.fill((a, a, a))
            surface.blit(self.flare, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.falpha > 0:
            a = 256 - int(self.falpha)
            self.flare.fill((a, a, a))
            surface.blit(self.flare, (0, 0), special_flags=pygame.BLEND_MULT)

class Delay(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS)]
        self.enter_pressed = False
        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((255, 255, 255))
        self.ftarget = 0
        self.falpha = 0
        self.controls = self.game.load_image("controls.png")
        self.age = 0
        self.duration = 3

    def update(self, dt, events):
        super().update(dt, events)
        for item in self.objects:
            item.update(dt, events)

        self.age += dt
        self.controls.set_alpha(max(0, min(255, min(self.age*300, (self.duration - self.age)*300))))

        if self.age > self.duration:
            self.is_over = True

    def next_scene(self):
        return Title(self.game)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((255, 255, 255))
        #surface.blit(self.controls, (0, 0))


class Instructions(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS)]
        self.enter_pressed = False
        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((255, 255, 255))
        self.ftarget = 0
        self.falpha = 0
        self.controls = self.game.load_image("controls.png")
        self.age = 0
        self.duration = 5

    def update(self, dt, events):
        super().update(dt, events)
        for item in self.objects:
            item.update(dt, events)

        self.age += dt
        self.controls.set_alpha(max(0, min(255, min(self.age*300, (self.duration - self.age)*300))))

        if self.age > self.duration:
            self.is_over = True

    def next_scene(self):
        return LevelScene(self.game)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((255, 255, 255))
        surface.blit(self.controls, (0, 0))


class Logo(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.objects = [Background(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Walls(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Curtains(game, c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2),
                        Piano(game, *c.PIANO_POS),
                        Bench(game, *c.BENCH_POS)]
        self.enter_pressed = False
        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((0, 0, 0))
        self.ftarget = 0
        self.falpha = 0
        self.controls = pygame.transform.scale2x(self.game.load_image("star_fish.png"))
        self.age = 0
        self.duration = 3

    def update(self, dt, events):
        super().update(dt, events)
        for item in self.objects:
            item.update(dt, events)

        self.age += dt
        self.controls.set_alpha(max(0, min(255, min(self.age*500, (self.duration - self.age)*500))))

        if self.age > self.duration:
            self.is_over = True

    def next_scene(self):
        return Title(self.game)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        surface.blit(self.controls, (c.WINDOW_WIDTH//2 - self.controls.get_width()//2, c.WINDOW_HEIGHT//2 - self.controls.get_height()//2))