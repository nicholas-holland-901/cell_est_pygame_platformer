import pygame


class Player:
    # Constants
    WIDTH = 20
    HEIGHT = 20
    FRICTION = -0.2
    ACCELERATION = 0.9
    DASH_POWER = 5
    DASH_LENGTH = 400
    GRAVITY_FORCE = 0.4
    GRAVITY_ACCELERATION = 0.7

    def __init__(self, start_x=0, start_y=0):
        self.pos = pygame.Vector2(start_x, start_y)
        self.vel = pygame.Vector2(0, 0)
        self.accel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, 0)
        self.grounded = False
        self.jumping = False
        self.can_dash = True
        self.dashing = False
        self.trying_to_dash = False
        self.in_water = False
        self.time_since_last_jump = 0
        self.time_since_last_dash = 0
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.WIDTH, self.HEIGHT)

    def move(self):
        self.accel = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()

        self.direction = pygame.Vector2(0, 0)

        if keys[pygame.K_a]:
            self.accel.x = -self.ACCELERATION
        if keys[pygame.K_d]:
            self.accel.x = self.ACCELERATION

        if keys[pygame.K_w] and self.grounded:
            # Jump
            self.time_since_last_jump = pygame.time.get_ticks()
            self.jumping = True
            self.grounded = False
            self.vel.y = -6

        # Holding down jump makes it longer
        if keys[pygame.K_w] and not self.grounded and self.jumping and pygame.time.get_ticks() - self.time_since_last_jump < 200:
            self.vel.y = -6

        self.trying_to_dash = False

        if keys[pygame.K_LEFT]:
            trying_to_dash = True
            self.direction.x = 1
        if keys[pygame.K_RIGHT]:
            trying_to_dash = True
            self.direction.x = -1
        if keys[pygame.K_UP]:
            trying_to_dash = True
            self.direction.y = 1
        if keys[pygame.K_DOWN]:
            trying_to_dash = True
            self.direction.y = -1

        if self.trying_to_dash and self.can_dash:
            # Dash
            self.vel = pygame.Vector2(0, 0)
            self.dashing = True
            self.can_dash = False
            self.grounded = False
            self.time_since_last_dash = pygame.time.get_ticks()

        # Holding down dash makes it longer
        if self.trying_to_dash and not self.grounded and self.dashing and pygame.time.get_ticks() - self.time_since_last_dash < self.DASH_LENGTH:
            self.vel.x = -self.DASH_POWER * self.direction.x * 2
        else:
            self.dashing = False

        # Apply horizontal movement
        self.accel.x += self.vel.x * self.FRICTION
        self.vel.x += self.accel
        self.pos.x += self.vel.x + 0.5 * self.accel.x

    def apply_gravity(self):
        # Apply gravity if not on the ground
        if not self.grounded and not self.dashing and not self.in_water:
            self.vel.y += self.GRAVITY_FORCE
            self.pos.y += self.vel.y + self.GRAVITY_ACCELERATION * self.accel.y
        elif self.grounded and not self.dashing and not self.in_water:
            self.vel.y = 0
            self.accel.y = 0
        elif self.in_water and not self.dashing:
            self.vel.y -= self.GRAVITY_FORCE * 0.5
            self.pos.y += self.vel.y + self.GRAVITY_ACCELERATION * self.accel.y * 0.5

        # Holding down dash makes it longer
        if self.trying_to_dash and not self.grounded and self.dashing and pygame.time.get_ticks() - self.time_since_last_dash < self.DASH_LENGTH:
            self.vel.y = -self.DASH_POWER * self.direction.y
            self.pos.y += self.vel.y
        else:
            self.dashing = False
