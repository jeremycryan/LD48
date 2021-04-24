##!/usr/bin/env python3

import pygame
import math

from primitives import GameObject, Pose
import random

import constants as c
from primitives import Pose


class Particle(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age = 0
        self.duration = None
        self.dead = False

    def get_alpha(self):
        return 255

    def get_scale(self):
        return 1

    def through(self, loading=1):
        """ Increase loading argument to 'frontload' the animation. """
        if self.duration is None:
            return 0
        else:
            return 1 - (1 - self.age / self.duration)**loading

    def update(self, dt, events):
        self.age += dt
        if self.duration and self.age > self.duration:
            self.destroy()

    def destroy(self):
        self.dead = True

class NoteParticle(Particle):
    def __init__(self, game, parent):
        super().__init__(game)
        self.color = parent.color
        self.duration = 1.2
        self.age = random.random() * 0.5
        self.radius = 7 * self.get_scale()
        angle = random.random() * 360
        offset = Pose((parent.radius - self.radius, 0), 0)
        offset.rotate_position(angle)
        self.velocity = offset * (random.random()**2 * 75 + 15)
        self.pose = Pose((parent.x, c.NOTE_TARGET_Y), 0) + offset

    def get_scale(self):
        return 1 - self.through()

    def get_alpha(self):
        return 255

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt
        self.radius = 7 * self.get_scale()
        self.velocity *= 0.01**dt

    def draw(self, surf, offset=(0, 0)):
        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        pygame.draw.circle(surf, self.color, (x, y), self.radius)


class NoteExplosion(Particle):
    def __init__(self, game, parent):
        super().__init__(game)
        self.pose = Pose((parent.x, c.NOTE_TARGET_Y), 0)
        self.radius = parent.radius
        self.color = parent.color
        self.duration = 0.6

    def get_scale(self):
        return 1 + self.through(3) * 4

    def get_alpha(self):
        return (1 - self.through(3)) * 255

    def draw(self, surface, offset=(0, 0)):
        x = self.pose.x + offset[0] - self.radius * self.get_scale()
        y = self.pose.y + offset[1] - self.radius * self.get_scale()
        r = int(self.radius * self.get_scale())
        surf = pygame.Surface((2*r, 2*r))
        surf.fill((0, 0, 0))
        pygame.draw.circle(surf, self.color, (r, r), r)
        surf.set_colorkey((0, 0, 0))
        surf.set_alpha(self.get_alpha())
        surface.blit(surf, (x, y))