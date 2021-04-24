import pygame


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

FULLSCREEN = False

GAME_TITLE = "FADE"

FPS = 60
SIM_FPS = 60

NOTES = 1, 2, 3, 4, 5, 6, 7, 8

BEATS_BEFORE_SONG = 8

NOTE_TARGET_Y = 60
BEAT_HEIGHT = 80
TARGET_MARGIN = 75
TARGET_SPACING = 50

DEFAULT_CONTROLS = {pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4,
                    pygame.K_7: 5,
                    pygame.K_8: 6,
                    pygame.K_9: 7,
                    pygame.K_0: 8}