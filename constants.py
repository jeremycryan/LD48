import pygame
import os


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

FULLSCREEN = False

GAME_TITLE = "FADE"

FPS = 60
SIM_FPS = 60

NOTES = 1, 2, 3, 4, 5, 6, 7, 8

BEATS_BEFORE_SONG = 8

NOTE_TARGET_Y = 60
BEAT_HEIGHT = 100
TARGET_MARGIN = 80
TARGET_SPACING = 60

NOTE_COLORS = {1: (255, 255, 0),
              2: (255, 0, 0),
               3: (0, 255, 255),
               4: (0, 0, 255),
               5: (255, 0, 255),
               6: (0, 255, 0),
               7: (255, 128, 0),
               8: (128, 0, 255)}

for note in NOTE_COLORS:
    NOTE_COLORS[note] = [(col + 255*2)/3 for col in NOTE_COLORS[note]]


DEFAULT_CONTROLS = {pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4,
                    pygame.K_7: 5,
                    pygame.K_8: 6,
                    pygame.K_9: 7,
                    pygame.K_0: 8}

PIANO_POS = WINDOW_WIDTH//2, int(WINDOW_HEIGHT*0.65)
BENCH_POS = WINDOW_WIDTH//2, int(WINDOW_HEIGHT*0.78)
LEFT_POS = WINDOW_WIDTH//2 - 53, int(WINDOW_HEIGHT*0.72)
RIGHT_POS = WINDOW_WIDTH - LEFT_POS[0], LEFT_POS[1]

def image_path(rel):
    return os.path.join("images", rel)

def sound_path(rel):
    return os.path.join("sounds", rel)

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0


SONG_1 = ["Q",[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          "E",[8],[],[],[5],[],[],[6],[7],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          [8],[],[],[5],[],[],[6],[7],[],[],[8],[7],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          [],[],[],[7],[],[8],[],[7],[],[],[],[6],[],[7],[],[5],[],[],[],[8],[],[],[7],[5],[],[],[],[],[],[],[],[],
          [],[],[],[7],[],[8],[],[7],[],[],[],[8],[],[],[6],[5],[],[],[],"S",[6],[7],"E",[8,5],[7,5],[6,5],[5],[],[7],[6],[5],[],[6],[],
          "Q",[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          "E",[],[],[],[],[],[],[8],[],[],[],[],[],[],[],[8],[],[]]

SONG_2 = ["Q",[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          "E",[8],[],[],[5],[],[],[6],[7],[],[],[],[],[],[],[],[],[8,6],[],[],[],[8,5],[],[],[],[7,5],[],[],[],[],[],[],[],
          [],[],[8],[7],[6],[5],[8],[7],[],[],"S",[5],[6],"E",[5],[8],[7],[6],[5],[],[],"S",[5],[6],"E",[7],[],[5,7],[],[6,8],[],[5,7],[],[5,6],[],[],[],[],
          [8],[7],[6],[5],[],[],[6],[7],[],[],[],[],[],[],[],[],[5,6,8],[5],[6],[8],[5,6,7],[5],[6],[7],[5,7,8],[],[],[],[],[],[],[],
          [],[],[8],[7],[6],[5],[8],[7],[],[],[8],[7],[6],[6],[5],[6],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],
          [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

QUARTER = "Q"
EIGHTH = "E"
SIXTEENTH = "S"

DIALOGUE_HEIGHT = int(WINDOW_HEIGHT*0.25)
DIALOGUE_THICKNESS = 100

def process_song(song):
    new = []
    mode = EIGHTH
    for item in song:
        if item in [QUARTER, EIGHTH, SIXTEENTH]:
            mode = item
        else:
            new.append(item)
            if mode == EIGHTH:
                new.append([])
            if mode == QUARTER:
                new += [[],[],[]]
    return new

SONG_1 = process_song(SONG_1)
SONG_2 = process_song(SONG_2)