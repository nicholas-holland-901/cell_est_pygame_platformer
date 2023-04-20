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
    DEFAULT_PLAYER_COLOR = (255, 100, 100)
    NO_DASH_PLAYER_COLOR = (100, 100, 255)

    def __init__(self, screen, start_x=0, start_y=0):
        self.pos = pygame.Vector2(start_x, start_y)
        self.vel = pygame.Vector2(0, 0)
        self.accel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, 0)
        self.screen = screen
        self.grounded = False
        self.jumping = False
        self.can_dash = True
        self.dashing = False
        self.trying_to_dash = False
        self.in_water = False
        self.ground_tiles = []
        self.water_tiles = []
        self.time_since_last_jump = 0
        self.time_since_last_dash = 0
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.WIDTH, self.HEIGHT)

    def update(self):
        self.move()
        self.player_horizontal_collisions()
        self.apply_gravity()
        self.player_vertical_collisions()
        self.draw_player()
        self.check_surroundings()

    def set_pos(self, x, y):
        self.pos = pygame.Vector2(x, y)

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
            self.trying_to_dash = True
            self.direction.x = 1
        if keys[pygame.K_RIGHT]:
            self.trying_to_dash = True
            self.direction.x = -1
        if keys[pygame.K_UP]:
            self.trying_to_dash = True
            self.direction.y = 1
        if keys[pygame.K_DOWN]:
            self.trying_to_dash = True
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
        self.vel += self.accel
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

    def player_horizontal_collisions(self):
        plr_hitbox = pygame.Rect(self.pos.x - 20, self.pos.y - 20, 20, 20)

        for tile in self.ground_tiles:
            pygame.draw.rect(self.screen, (100, 100, 100), tile)
            # Check horizontal collisions
            if pygame.Rect.colliderect(plr_hitbox, tile):
                if self.vel.x > 0:
                    self.vel.x = 0
                    self.accel.x = 0
                    self.pos.x = tile.left
                if self.vel.x < 0:
                    self.accel.x = 0
                    self.vel.x = 0
                    self.pos.x = tile.right + 20

    def player_vertical_collisions(self):
        plr_hitbox = pygame.Rect(self.pos.x - 20, self.pos.y - 20, 20, 20)

        for tile in self.ground_tiles:
            # Check vertical collisions
            if pygame.Rect.colliderect(plr_hitbox, tile):
                if self.vel.y > 0:
                    grounded = True
                    self.accel.y = 0
                    self.vel.y = 0
                    self.pos.y = tile.top
                if self.vel.y < 0:
                    self.vel.y = 0
                    self.accel.y = 0
                    self.pos.y = tile.bottom + 20

    def check_surroundings(self):
        jump_hitbox = pygame.Rect(self.pos.x - 20, self.pos.y - 5, 20, 6)
        any_collide = False
        water_collide = False
        for tile in self.ground_tiles:
            if pygame.Rect.colliderect(jump_hitbox, tile):
                any_collide = True
        for piece in self.water_tiles:
            if pygame.Rect.colliderect(jump_hitbox, piece):
                water_collide = True
        if any_collide:
            self.grounded = True
            self.can_dash = True
        else:
            self.grounded = False
        if water_collide:
            self.in_water = True
        else:
            self.in_water = False
        if self.in_water:
            self.can_dash = True

    def draw_player(self):
        # Draw player at Vector2 location
        if self.can_dash:
            pygame.draw.rect(self.screen, self.DEFAULT_PLAYER_COLOR, [self.pos.x - 20, self.pos.y - 20, 20, 20])
        else:
            pygame.draw.rect(self.screen, self.NO_DASH_PLAYER_COLOR, [self.pos.x - 20, self.pos.y - 20, 20, 20])
