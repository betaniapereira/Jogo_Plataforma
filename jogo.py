from pgzero.builtins import Actor, keyboard, Rect, music, sounds
import random

WIDTH = 800
HEIGHT = 600
TITLE = "The Knight"

GRAVITY = 0.5
JUMP_STRENGTH = -12
MOVE_SPEED = 5
TILE_SIZE = 40

game_state = 'menu'
sound_on = True
score = 0

player = None
platforms = []
enemies = []
background_walls = []
decorations = []

background = Actor("background")

class Player(Actor):
    def __init__(self, pos):
        self.idle_frames = [f"player_idle{i}" for i in range(4)]
        self.run_frames = [f"player_run{i}" for i in range(6)]
        self.jump_frame = "player_jump"
        
        super().__init__(self.idle_frames[0], pos, anchor=('center', 'bottom'))

        self.vy = 0 
        self.on_ground = False 
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.state = 'jump' 
        self.flip_x = False

    def animate(self):
        if self.state == 'idle':
            current_animation = self.idle_frames
            self.animation_speed = 8
        elif self.state == 'run':
            current_animation = self.run_frames
            self.animation_speed = 4
        else: 
            self.image = self.jump_frame
            return

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(current_animation)
            self.image = current_animation[self.current_frame]

    def update_physics(self, platforms):
        is_moving = False
        if keyboard.left:
            self.x -= MOVE_SPEED
            self.flip_x = True
            is_moving = True
        if keyboard.right:
            self.x += MOVE_SPEED
            self.flip_x = False
            is_moving = True
        if keyboard.space and self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False
            if sound_on:
                sounds.jump.play()

        if not self.on_ground:
            self.vy += GRAVITY
    
        self.y += self.vy

        platform_under_player = None
        self.on_ground = False
        for p in platforms:
            if self.colliderect(p):
                if self.vy >= 0:
                    self.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                    platform_under_player = p
                    self.y += 1
                    break 

        if self.on_ground and isinstance(platform_under_player, MovingPlatform):
            self.x += platform_under_player.speed * platform_under_player.direction

        if not self.on_ground:
            self.state = 'jump'
        elif is_moving:
            self.state = 'run'
        else:
            self.state = 'idle'
            
        if self.left < 0: self.left = 0
        if self.right > WIDTH: self.right = WIDTH
        
    def update(self, platforms):
        self.update_physics(platforms)
        self.animate()

class Enemy(Actor):
    def __init__(self, pos, platform):
        self.idle_frames = [f"enemy_idle{i}" for i in [0, 2, 3, 4, 5, 6, 7, 8]]
        super().__init__(self.idle_frames[0], pos)
        self.speed = 1
        self.patrol_left = platform.left + self.width / 2
        self.patrol_right = platform.right - self.width / 2
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10
        self.flip_x = False

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.current_frame]

    def update(self):
        self.x += self.speed
        if self.x > self.patrol_right or self.x < self.patrol_left:
            self.speed *= -1
            self.flip_x = not self.flip_x
        self.animate()

class MovingPlatform(Actor):
    def __init__(self, image, pos, end_pos, speed):
        super().__init__(image, pos)
        self.start_pos = pos
        self.end_pos = end_pos
        self.speed = speed
        self.direction = 1 

    def update(self):
        self.x += self.speed * self.direction
        if self.direction == 1 and self.x >= self.end_pos[0]:
            self.direction = -1
        elif self.direction == -1 and self.x <= self.start_pos[0]:
            self.direction = 1

def setup_game():
    global platforms, enemies, player, score, game_over, goal, background_walls, decorations
    platforms = []
    enemies = []
    decorations = []
    background_walls = []
    score = 0
    game_over = False

    platforms.append(Actor("platform5", topleft=(50, 550)))
    platforms.append(Actor("platform2", topleft=(178, 550)))
    platforms.append(Actor("platform2", center=(400, 480)))

    moving_plat = MovingPlatform("platform4", pos=(500, 400), end_pos=(700, 400), speed=1.5)
    platforms.append(moving_plat)

    enemy_plat = Actor("platform2", center=(600, 300))
    platforms.append(enemy_plat)
    enemies.append(Enemy(pos=(enemy_plat.x, enemy_plat.top - 20), platform=enemy_plat))

    platforms.append(Actor("platform3", center=(750, 320)))
    platforms.append(Actor("platform5", center=(500, 240)))
    platforms.append(Actor("platform4", center=(400, 220)))
    platforms.append(Actor("platform5", center=(250, 180)))

    goal_platform = Actor("platform2", center=(100, 120))
    platforms.append(goal_platform)
    
    for p in platforms:
        start_x = int(p.left // TILE_SIZE) * TILE_SIZE
        end_x = int(p.right // TILE_SIZE) * TILE_SIZE
        start_y = int(p.bottom // TILE_SIZE) * TILE_SIZE

        for y in range(start_y, HEIGHT, TILE_SIZE):
            for x in range(start_x, end_x + TILE_SIZE, TILE_SIZE):
                wall_image = "wall_gold0" if p.y < HEIGHT / 2 else "wall0"
                wall_tile = Actor(wall_image, topleft=(x, y))
                background_walls.append(wall_tile)

    player = Player(pos=(100, 500)) 
    goal = Actor("goal", midbottom=goal_platform.midtop) 

BUTTON_WIDTH = 250
BUTTON_HEIGHT = 60
BUTTON_X = (WIDTH - BUTTON_WIDTH) / 2
start_button_rect = Rect((BUTTON_X, HEIGHT / 2 - 80), (BUTTON_WIDTH, BUTTON_HEIGHT))
sound_button_rect = Rect((BUTTON_X, HEIGHT / 2), (BUTTON_WIDTH, BUTTON_HEIGHT))
quit_button_rect = Rect((BUTTON_X, HEIGHT / 2 + 80), (BUTTON_WIDTH, BUTTON_HEIGHT))
restart_button_rect = Rect(0, 0, 250, 60)
restart_button_rect.center = (WIDTH / 2, HEIGHT / 2 + 130)

def draw():
    screen.clear()
    background.draw()

    if game_state == 'menu':
        screen.draw.text(TITLE, center=(WIDTH / 2, HEIGHT / 4), fontsize=60, color="white", owidth=0.1, ocolor="white")
        screen.draw.filled_rect(start_button_rect, 'green')
        screen.draw.text("Start", center=start_button_rect.center, fontsize=40, color="white")
        sound_button_text = "Music: ON" if sound_on else "Music: OFF"
        screen.draw.filled_rect(sound_button_rect, 'orange')
        screen.draw.text(sound_button_text, center=sound_button_rect.center, fontsize=40, color="white")
        screen.draw.filled_rect(quit_button_rect, 'red')
        screen.draw.text("Quit", center=quit_button_rect.center, fontsize=40, color="white")
    
    elif game_state in ['playing', 'win', 'lose']:
        for wall in background_walls: wall.draw()
        for d in decorations: d.draw()
        for p in platforms: p.draw()
        for e in enemies: e.draw()
        if goal: goal.draw()
        if player: player.draw()

        screen.draw.text(f"Score: {int(score)}", topleft=(10, 10), fontsize=40, color="white", owidth=1, ocolor="black")
        
        if game_state == 'win':
            screen.draw.text("YOU WIN!", center=(WIDTH / 2, HEIGHT / 2), fontsize=100, color="yellow", owidth=1, ocolor="black")
            screen.draw.text(f"Final Score: {int(score)}", center=(WIDTH / 2, HEIGHT / 2 + 60), fontsize=50, color="white")
            screen.draw.filled_rect(restart_button_rect, 'blue')
            screen.draw.text("Play Again", center=restart_button_rect.center, fontsize=40, color="white")
        
        elif game_state == 'lose':
            screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2), fontsize=100, color="red", owidth=1, ocolor="black")
            screen.draw.text(f"Final Score: {int(score)}", center=(WIDTH / 2, HEIGHT / 2 + 60), fontsize=50, color="white")
            screen.draw.filled_rect(restart_button_rect, 'blue')
            screen.draw.text("Play Again", center=restart_button_rect.center, fontsize=40, color="white")

def update(dt):
    global score, game_state
    if game_state != 'playing':
        return
    
    for p in platforms:
        if hasattr(p, 'update'): 
            p.update()

    player.update(platforms) 
    for e in enemies: e.update()

    if goal and player.colliderect(goal):
        game_state = 'win'
        return

    for e in enemies:
        if player.colliderect(e):
            if sound_on: sounds.hit.play()
            game_state = 'lose'
            return

    score += dt * 10 

    if player.top > HEIGHT:
        if sound_on: sounds.hit.play()
        game_state = 'lose'

def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == 'menu':
        if start_button_rect.collidepoint(pos):
            game_state = 'playing'
            setup_game()
        if sound_button_rect.collidepoint(pos):
            sound_on = not sound_on
            update_music()
        if quit_button_rect.collidepoint(pos):
            quit()
    elif game_state in ['win', 'lose']:
        if restart_button_rect.collidepoint(pos):
            game_state = 'playing'
            setup_game()

def update_music():
    if sound_on and not music.is_playing('background'):
        music.play('background')
    elif not sound_on:
        music.stop()

setup_game()
update_music()