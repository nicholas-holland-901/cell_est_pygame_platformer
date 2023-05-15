import pygame

class Player:
    # Constants
    WIDTH = 20
    HEIGHT = 20
    FRICTION = -0.2
    ACCELERATION = 0.9
    DASH_POWER = -5
    DASH_LENGTH = 400
    GRAVITY_FORCE = 0.4
    MAX_GRAVITY = 8
    GRAVITY_ACCELERATION = 0.7
    WALLJUMP_COOLDOWN = 100
    DEFAULT_PLAYER_COLOR = (255, 100, 100)
    NO_DASH_PLAYER_COLOR = (100, 100, 255)

    def __init__(self, screen, start_x=0, start_y=0):
        self.screen = screen
        # Movement vectors
        self.pos = pygame.Vector2(start_x, start_y)
        self.vel = pygame.Vector2(0, 0)
        self.accel = pygame.Vector2(0, 0)
        # Wall jump side, 0 = Left wall, 1 = Right wall
        self.wall_jump = 0
        # States
        self.grounded = False
        self.jumping = False
        self.walljumping = False
        self.can_dash = True
        self.dashing = False
        self.trying_to_dash = False
        self.just_pressed_jump = False
        self.in_water = False
        self.can_move = True
        # Tiles
        self.ground_tiles = []
        self.water_tiles = []
        self.spikes = []
        self.spinners = []
        # Timers
        self.time_since_last_jump = 0
        self.time_since_last_dash = 0
        self.time_since_last_walljump = 0
        # Player Body
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.WIDTH, self.HEIGHT)

    def update(self, window):
        # Constantly move player and update position
        if self.can_move:
            # Move player horizontally and check horizontal collisions
            self.move()
            self.player_horizontal_collisions()
            # Move player vertically and check vertical collisions
            self.apply_gravity()
            self.player_vertical_collisions()
            # Draw player and check state
            self.draw_player(window)
            self.check_surroundings()

    def set_pos(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def move(self):
        # Reset acceleration and get input
        self.accel = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()

        # Can't move towards wall while wall jumping
        if keys[pygame.K_a] and not self.walljumping and self.wall_jump != 2:
            self.accel.x = -self.ACCELERATION
        if keys[pygame.K_d] and not self.walljumping and self.wall_jump != 1:
            self.accel.x = self.ACCELERATION

        # Only jump if on the ground
        if keys[pygame.K_w] and self.grounded:
            self.time_since_last_jump = pygame.time.get_ticks()
            self.jumping = True
            self.grounded = False
            self.vel.y = -6

        # Holding down the jump button makes the player jump higher
        if keys[pygame.K_w] and not self.grounded and self.jumping and pygame.time.get_ticks() - self.time_since_last_jump < 200:
            self.vel.y = -6

        # Walljump cooldown to prevent walljump spam
        if self.time_since_last_walljump != 0 and pygame.time.get_ticks() - self.time_since_last_walljump > self.WALLJUMP_COOLDOWN:
            self.time_since_last_walljump = 0
            self.wall_jump = 0
            self.walljumping = False

        # Wall jump while against wall
        if keys[pygame.K_w] and self.wall_jump != 0 and not self.grounded and not self.just_pressed_jump:
            if not self.walljumping:
                self.time_since_last_walljump = pygame.time.get_ticks()
            self.walljumping = True
            self.grounded = False
            self.vel.y = -6
            if self.wall_jump == 1:
                # Jump off wall that is on the right
                self.vel.x = -10
            elif self.wall_jump == 2:
                # Jump off wall that is on the left
                self.vel.x = 10

        self.trying_to_dash = False

        if keys[pygame.K_SPACE]:
            self.trying_to_dash = True

        if self.trying_to_dash and self.can_dash:
            # Dash
            self.vel.y = 0
            self.dashing = True
            self.can_dash = False
            self.grounded = False
            self.time_since_last_dash = pygame.time.get_ticks()

        # Apply horizontal movement
        self.accel.x += self.vel.x * self.FRICTION
        self.vel += self.accel
        self.pos.x += self.vel.x + 0.5 * self.accel.x

        if keys[pygame.K_w]:
            self.just_pressed_jump = True
        else:
            self.just_pressed_jump = False

    def apply_gravity(self):
        # Apply gravity if not on the ground
        if not self.grounded and not self.dashing and not self.in_water and self.vel.y < self.MAX_GRAVITY and not self.walljumping:
            # Normal Gravity
            self.vel.y += self.GRAVITY_FORCE
            self.pos.y += self.vel.y + self.GRAVITY_ACCELERATION * self.accel.y
        elif not self.grounded and not self.dashing and not self.in_water and self.vel.y >= self.MAX_GRAVITY and not self.walljumping:
            # If reached terminal velocity
            self.vel.y = self.MAX_GRAVITY
            self.pos.y += self.vel.y
        elif self.grounded and not self.dashing and not self.in_water:
            # No gravity while on the ground
            self.vel.y = 0
            self.accel.y = 0
        elif self.in_water and not self.dashing:
            # Gravity while in water, slowly float
            if self.vel.y < 1:
                # Normal water force
                self.vel.y -= self.GRAVITY_FORCE * 0.07
                self.pos.y += self.vel.y + self.GRAVITY_ACCELERATION * self.accel.y * 0.5
            else:
                # Increase force of water if falling kinda fast
                self.vel.y -= self.GRAVITY_FORCE
                self.pos.y += self.vel.y + self.GRAVITY_ACCELERATION * self.accel.y * 0.5
        # Holding down dash makes it longer
        if self.trying_to_dash and not self.grounded and self.dashing and pygame.time.get_ticks() - self.time_since_last_dash < self.DASH_LENGTH:
            self.vel.y = self.DASH_POWER
            self.pos.y += self.vel.y
        else:
            self.dashing = False

        if self.walljumping:
            self.vel.y = -6
            self.pos.y += self.vel.y

    def player_horizontal_collisions(self):
        plr_hitbox = pygame.Rect(self.pos.x - 20, self.pos.y - 20, 20, 20)

        for tile in self.ground_tiles:
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
        # Player hitboxes
        jump_hitbox = pygame.Rect(self.pos.x - 20, self.pos.y - 5, 20, 6)
        left_wall_hitbox = pygame.Rect(self.pos.x - 23, self.pos.y - 20, 3, 20)
        right_wall_hitbox = pygame.Rect(self.pos.x, self.pos.y - 20, 3, 20)

        if not self.walljumping:
            self.wall_jump = 0

        any_collide = False
        water_collide = False
        for tile in self.ground_tiles:
            if pygame.Rect.colliderect(jump_hitbox, tile):
                any_collide = True
            if pygame.Rect.colliderect(right_wall_hitbox, tile):
                self.wall_jump = 1
            if pygame.Rect.colliderect(left_wall_hitbox, tile):
                self.wall_jump = 2
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

    def draw_player(self, window):
        # Draw player at Vector2 location
        if self.can_dash:
            pygame.draw.rect(self.screen, self.DEFAULT_PLAYER_COLOR, [self.pos.x - 20, self.pos.y - 20, 20, 20])
        else:
            pygame.draw.rect(self.screen, self.NO_DASH_PLAYER_COLOR, [self.pos.x - 20, self.pos.y - 20, 20, 20])
            pass