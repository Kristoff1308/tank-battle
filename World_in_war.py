from tkinter.font import BOLD

import pygame
import math
import random
import json
import os
from PIL import Image

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")
clock = pygame.time.Clock()
FPS = 60
GREEN = pygame.Color('darkgreen')
GRAY = pygame.Color('dimgray')
DARK_GRAY = pygame.Color('gray25')
BLACK = pygame.Color('black')
WALL_COLOR = pygame.Color('saddlebrown')
WALL_BORDER = pygame.Color('sienna')
ENEMY_COLOR = pygame.Color('firebrick')
ENEMY_DARK = pygame.Color('darkred')
RED = pygame.Color('red')
GREEN_HP = pygame.Color('limegreen')
BLUE = pygame.Color('dodgerblue')
WHITE = pygame.Color('white')
YELLOW = pygame.Color('gold')
LIGHT_GRAY = pygame.Color('#e6f2e6')
MENU_GREEN = pygame.Color('#2e7d32')
BUTTON_GREEN = pygame.Color('#4CAF50')
BUTTON_GREEN_HOVER = pygame.Color('#45a049')
BUTTON_GRAY = pygame.Color((240, 240, 240, 200))
BUTTON_GRAY_HOVER = pygame.Color((217, 217, 217, 220))
BUTTON_RED = pygame.Color('#f44336')
BUTTON_RED_HOVER = pygame.Color('#d32f2f')
FONT = pygame.font.Font(None, 48)
SMALL_FONT = pygame.font.Font(None, 32)
TINY_FONT = pygame.font.Font(None, 24)
HIGH_SCORE_FILE = "highscore.json"

menu_background = None
try:
    bg_path = os.path.join("images", "input_bg.jpg")
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        menu_background = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 80))
        menu_background.blit(dark_overlay, (0, 0))
except Exception:
    pass
game_background = None
try:
    game_bg_path = os.path.join("images", "game_bg.jpg")
    if os.path.exists(game_bg_path):
        img = Image.open(game_bg_path).convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        game_background = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        dark_overlay_game = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_overlay_game.fill((0, 0, 0, 60))
        game_background.blit(dark_overlay_game, (0, 0))
except Exception:
    pass
wall_texture = None
try:
    wall_path = os.path.join("images", "wall_stone.png")
    if os.path.exists(wall_path):
        img = Image.open(wall_path).convert("RGBA")
        img = img.resize((64, 64), Image.Resampling.LANCZOS)
        wall_texture = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
except Exception:
    pass
input_name_background = None
try:
    input_bg_path = os.path.join("images", "menu_bg.jpg")  
    if os.path.exists(input_bg_path):
        img = Image.open(input_bg_path).convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        input_name_background = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 90))
        input_name_background.blit(dark_overlay, (0, 0))
except Exception:
    pass
engine_sound = None
shot_sound = None
try:
    engine_path = os.path.join("sound", "engine stand.wav")
    if os.path.exists(engine_path):
        engine_sound = pygame.mixer.Sound(engine_path)
        engine_sound.set_volume(0.3)
    shot_path = os.path.join("sound", "semiautorifle3.wav")
    if os.path.exists(shot_path):
        shot_sound = pygame.mixer.Sound(shot_path)
        shot_sound.set_volume(0.4)
except Exception:
    pass
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"name": "---", "score": 0}
    return {"name": "---", "score": 0}
def save_high_score(name, score):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"name": name, "score": score}, f)
def draw_text(text, x, y, color=WHITE, font=FONT, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y) if center else (x, y))
    screen.blit(surf, rect)
def draw_button(x, y, w, h, text, color, hover_color, hover=False):
    rect = pygame.Rect(x, y, w, h)
    fill = hover_color if hover else color
    if len(fill) == 4:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, fill, (0, 0, w, h), border_radius=6)
        pygame.draw.rect(s, (0, 0, 0, 200), (0, 0, w, h), 2, border_radius=6)
        screen.blit(s, (x, y))
    else:
        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
    text_color = WHITE if color in (BUTTON_GREEN, BUTTON_RED) else BLACK
    draw_text(text, x + w // 2, y + h // 2, text_color, SMALL_FONT)
    return rect
class Bullet:
    def __init__(self, x, y, angle, owner=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 14
        self.active = True
        self.radius = 5
        self.owner = owner
    def update(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y -= self.speed * math.sin(rad)
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)
    def check_collision(self, wall):
        return wall.rect.collidepoint(self.x, self.y)
class Wall:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.collision_margin = 2
    def draw(self, surface):
        if wall_texture:
            tex_w = wall_texture.get_width()
            tex_h = wall_texture.get_height()     
            for dy in range(0, self.h, tex_h):
                for dx in range(0, self.w, tex_w):              
                    clip_w = min(tex_w, self.w - dx)
                    clip_h = min(tex_h, self.h - dy)
                    if clip_w == tex_w and clip_h == tex_h:               
                        surface.blit(wall_texture, (self.x + dx, self.y + dy))
                    else:
                        cropped = wall_texture.subsurface((0, 0, clip_w, clip_h))
                        surface.blit(cropped, (self.x + dx, self.y + dy))
        pygame.draw.rect(surface, BLACK, self.rect, 2)
    def check_collision(self, tank):
        tank_rect = pygame.Rect(
            tank.x - tank.radius - self.collision_margin,
            tank.y - tank.radius - self.collision_margin,
            tank.radius * 2 + self.collision_margin * 2,
            tank.radius * 2 + self.collision_margin * 2)
        return tank_rect.colliderect(self.rect)
        return tank_rect.colliderect(self.rect)
class HealthPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.active = True
    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (100, 180, 255), (int(self.x), int(self.y)), self.radius - 3)
    def check_collision(self, tank):
        return math.hypot(self.x - tank.x, self.y - tank.y) < tank.radius + self.radius
class Tank:
    def __init__(self, x, y, size="medium"):
        self.x = x
        self.y = y
        self.body_angle = 0
        self.turret_angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 4
        self.acceleration = 0.22
        self.deceleration = 0.12
        self.width = 32
        self.height = 48
        self.radius = 26
        self.track_offset = 0
        self.track_speed = 2
        self.health = 12
        self.max_health = 12
        self.color = GRAY
        self.dark_color = DARK_GRAY
        self.points = 0
        self.is_moving = False
        if size == "small":
            self.width = 24
            self.height = 36
            self.radius = 20
            self.max_speed = 5
            self.health = 1
            self.max_health = 1
            self.points = 5
        elif size == "medium":
            self.width = 32
            self.height = 48
            self.radius = 26
            self.max_speed = 4
            self.health = 2
            self.max_health = 2
            self.points = 10
        elif size == "large":
            self.width = 40
            self.height = 60
            self.radius = 32
            self.max_speed = 3
            self.health = 3
            self.max_health = 3
            self.points = 15
    def move(self, up, down, left, right, walls):
        orig_x = self.x
        orig_y = self.y
        if up:
            self.speed_y = max(self.speed_y - self.acceleration, -self.max_speed)
        if down:
            self.speed_y = min(self.speed_y + self.acceleration, self.max_speed)
        if left:
            self.speed_x = max(self.speed_x - self.acceleration, -self.max_speed)
        if right:
            self.speed_x = min(self.speed_x + self.acceleration, self.max_speed)
        if not up and not down:
            self.speed_y = self.speed_y * 0.95 if abs(self.speed_y) > 0.05 else 0
        if not left and not right:
            self.speed_x = self.speed_x * 0.95 if abs(self.speed_x) > 0.05 else 0
        self.x += self.speed_x
        collide_x = any(wall.check_collision(self) for wall in walls)
        if collide_x:
            self.x = orig_x
            self.speed_x = 0
        self.y += self.speed_y
        collide_y = any(wall.check_collision(self) for wall in walls)
        if collide_y:
            self.y = orig_y
            self.speed_y = 0
        speed = math.hypot(self.speed_x, self.speed_y)
        self.is_moving = speed > 0.15
        if speed > 0.15:
            self.body_angle = math.degrees(math.atan2(-self.speed_y, self.speed_x))
            self.turret_angle = self.body_angle
            self.track_offset = (self.track_offset + self.track_speed) % 16
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))
    def rotate_turret(self, direction):
        self.turret_angle += direction * 3
    def shoot(self):
        rad = math.radians(self.turret_angle)
        bx = self.x + math.cos(rad) * (self.height / 2 + 8)
        by = self.y - math.sin(rad) * (self.height / 2 + 8)
        if shot_sound:
            shot_sound.play()
        return Bullet(bx, by, self.turret_angle, self)
    def draw(self, surface):
        body_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(body_surf, self.color, (0, 0, self.width, self.height), border_radius=6)
        pygame.draw.rect(body_surf, self.dark_color, (0, 2, 4, self.height - 4))
        pygame.draw.rect(body_surf, self.dark_color, (self.width - 4, 2, 4, self.height - 4))
        for i in range(4):
            yp = 6 + i * 10 + self.track_offset
            if yp < self.height - 6:
                pygame.draw.rect(body_surf, BLACK, (1, yp, 2, 4))
                pygame.draw.rect(body_surf, BLACK, (self.width - 3, yp, 2, 4))
        rot_body = pygame.transform.rotate(body_surf, self.body_angle)
        surface.blit(rot_body, rot_body.get_rect(center=(int(self.x), int(self.y))).topleft)
        turret_surf = pygame.Surface((self.width // 1.5, self.width // 1.5), pygame.SRCALPHA)
        pygame.draw.circle(turret_surf, self.color, (self.width // 3, self.width // 3), self.width // 3)
        pygame.draw.rect(turret_surf, BLACK, (self.width // 3, 0, 6, self.height // 2))
        rot_turret = pygame.transform.rotate(turret_surf, self.turret_angle)
        surface.blit(rot_turret, rot_turret.get_rect(center=(int(self.x), int(self.y))).topleft)
        hp_w = self.radius * 2
        hp_h = 6
        hp_x = self.x - self.radius
        hp_y = self.y - self.radius - 12
        pygame.draw.rect(surface, RED, (hp_x, hp_y, hp_w, hp_h))
        pygame.draw.rect(surface, GREEN_HP, (hp_x, hp_y, int((self.health / self.max_health) * hp_w), hp_h))
    def take_damage(self):
        self.health -= 1
        return self.health <= 0
    def heal(self, amount=4):
        self.health = min(self.max_health, self.health + amount)
class EnemyTank(Tank):
    def __init__(self, x, y, size="medium", extra_hp=0):
        super().__init__(x, y, size)
        self.color = ENEMY_COLOR
        self.dark_color = ENEMY_DARK
        self.shoot_cooldown = 0
        self.move_timer = 0
        self.target_x = self.x
        self.target_y = self.y
        self.health += extra_hp
        self.max_health += extra_hp
    def update_ai(self, player, walls):
        self.move_timer += 1
        if self.move_timer > random.randint(90, 200):
            self.target_x = random.randint(120, WIDTH - 120)
            self.target_y = random.randint(120, HEIGHT - 120)
            self.move_timer = 0
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 12:
            angle = math.degrees(math.atan2(-dy, dx))
            diff = (angle - self.body_angle + 180) % 360 - 180
            if abs(diff) > 8:
                self.body_angle += 2 if diff > 0 else -2
            else:
                self.speed_x = math.cos(math.radians(self.body_angle)) * self.max_speed * 0.35
                self.speed_y = -math.sin(math.radians(self.body_angle)) * self.max_speed * 0.35
        else:
            self.speed_x *= 0.9
            self.speed_y *= 0.9
        dx_t = player.x - self.x
        dy_t = player.y - self.y
        self.turret_angle = math.degrees(math.atan2(-dy_t, dx_t))
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and math.hypot(dx_t, dy_t) < 720:
            self.shoot_cooldown = random.randint(130, 220)
            return self.shoot()
        orig_x, orig_y = self.x, self.y
        self.x += self.speed_x
        if any(w.check_collision(self) for w in walls):
            self.x = orig_x
            self.speed_x *= -0.4
        self.y += self.speed_y
        if any(w.check_collision(self) for w in walls):
            self.y = orig_y
            self.speed_y *= -0.4
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))
def create_walls(count, safe_x, safe_y, safe_dist):
    walls = []
    margin = 90
    min_gap = 80
    for _ in range(count):
        while True:
            w = random.randint(55, 170)
            h = random.randint(30, 75)
            x = random.randint(margin, WIDTH - w - margin)
            y = random.randint(margin, HEIGHT - h - margin)
            cx, cy = x + w / 2, y + h / 2
            if math.hypot(cx - safe_x, cy - safe_y) < safe_dist + max(w, h) / 2 + 25:
                continue
            overlap = False
            for w2 in walls:
                if math.hypot(cx - (w2.x + w2.w / 2), cy - (w2.y + w2.h / 2)) < (max(w, h) + max(w2.w, w2.h)) / 2 + min_gap:
                    overlap = True
                    break
            if not overlap:
                walls.append(Wall(x, y, w, h))
                break
    return walls
def spawn_enemy(walls, px, py, time, level):
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(60, WIDTH - 60), -60
    elif side == "bottom":
        x, y = random.randint(60, WIDTH - 60), HEIGHT + 60
    elif side == "left":
        x, y = -60, random.randint(60, HEIGHT - 60)
    else:
        x, y = WIDTH + 60, random.randint(60, HEIGHT - 60)
    if time < 1600:
        size = "small"
    elif time < 3200:
        size = random.choice(["small", "medium"])
    else:
        size = random.choice(["small", "medium", "large"])

    return EnemyTank(x, y, size, extra_hp=max(0, level - 1))
def spawn_health(walls, px, py):
    while True:
        x = random.randint(120, WIDTH - 120)
        y = random.randint(120, HEIGHT - 120)
        if math.hypot(x - px, y - py) < 180:
            continue
        if not any(w.rect.collidepoint(x, y) for w in walls):
            return HealthPickup(x, y)
def input_name_screen():
    text = "Player"
    while True:
        if input_name_background:
            screen.blit(input_name_background, (0, 0))
        else:
            screen.fill(LIGHT_GRAY)
        draw_text("ENTER YOUR NAME", WIDTH // 2, HEIGHT // 2 - 80, WHITE, FONT)
        draw_text(text, WIDTH // 2, HEIGHT // 2, WHITE, SMALL_FONT)
        draw_text("Press ENTER to confirm", WIDTH // 2, HEIGHT // 2 + 60, WHITE, SMALL_FONT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text.strip() or "Player"
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 12:
                    text += event.unicode
        pygame.display.flip()
        clock.tick(FPS)
def show_highscore_screen():
    hs = load_high_score()
    while True:
        screen.fill(LIGHT_GRAY)
        draw_text("HIGH SCORE", WIDTH // 2, HEIGHT // 2 - 80, MENU_GREEN)
        draw_text(f"Score: {hs['score']}", WIDTH // 2, HEIGHT // 2 - 20, BLACK, SMALL_FONT)
        draw_text(f"Player: {hs['name']}", WIDTH // 2, HEIGHT // 2 + 20, BLACK, SMALL_FONT)
        draw_text("Press ESC to go back", WIDTH // 2, HEIGHT // 2 + 80, BLACK, TINY_FONT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)
def show_rules_screen():
    rules = [
        "CONTROLS:",
        "Arrow Keys - Move",
        "Q / E - Rotate Turret",
        "Spacebar - Shoot",
        "ESC - Return to Menu",
        "",
        "POINTS:",
        "Small Tank: 5",
        "Medium Tank: 10",
        "Large Tank: 15",
        "",
        "Blue Circles - Restore Health"
    ]
    while True:
        screen.fill(LIGHT_GRAY)
        draw_text("GAME RULES", WIDTH // 2, 60, MENU_GREEN)
        y = 120
        for line in rules:
            draw_text(line, WIDTH // 2, y, BLACK, SMALL_FONT)
            y += 35
        draw_text("Press ESC to go back", WIDTH // 2, HEIGHT - 60, BLACK, TINY_FONT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)
def show_result_screen(score, player_name):
    hs = load_high_score()
    new_record = score > hs["score"]
    if new_record:
        save_high_score(player_name, score)
    while True:
        screen.fill(LIGHT_GRAY)
        draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 100, RED)
        draw_text(f"Your Score: {score}", WIDTH // 2, HEIGHT // 2 - 30, BLACK, SMALL_FONT)
        if new_record:
            draw_text("NEW HIGH SCORE!", WIDTH // 2, HEIGHT // 2 + 20, YELLOW, SMALL_FONT)
        else:
            draw_text(f"High Score: {hs['score']} ({hs['name']})", WIDTH // 2, HEIGHT // 2 + 20, BLACK, SMALL_FONT)
        draw_text("Press ESC to return to menu", WIDTH // 2, HEIGHT // 2 + 80, BLACK, TINY_FONT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)
def game_loop(player_name):
    player_tank = Tank(WIDTH // 2, HEIGHT // 2)
    walls = create_walls(12, player_tank.x, player_tank.y, player_tank.radius + 40)
    enemies = []
    bullets = []
    pickups = []
    game_over = False
    level = 1
    next_level_time = 600
    max_enemies = 1
    spawn_timer = 0
    heal_timer = 0
    game_time = 0
    score = 0
    engine_playing = False
    while True:
        clock.tick(FPS)
        if game_background:
            screen.blit(game_background, (0, 0))
        else:
            screen.fill(GREEN)
        game_time += 1
        if game_time >= next_level_time:
            level += 1
            next_level_time += 600
            max_enemies = min(8, 1 + level - 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if engine_sound and engine_playing:
                        engine_sound.stop()
                    return score
                if not game_over and event.key == pygame.K_SPACE:
                    bullets.append(player_tank.shoot())
        if not game_over:
            keys = pygame.key.get_pressed()
            player_tank.move(keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT], walls)
            if engine_sound:
                if player_tank.is_moving and not engine_playing:
                    engine_sound.play(-1)
                    engine_playing = True
                elif not player_tank.is_moving and engine_playing:
                    engine_sound.stop()
                    engine_playing = False
            if keys[pygame.K_q]:
                player_tank.rotate_turret(1)
            if keys[pygame.K_e]:
                player_tank.rotate_turret(-1)
            if len(enemies) < max_enemies:
                spawn_timer += 1
                spawn_delay = max(50, 110 - level * 7)
                if spawn_timer > spawn_delay:
                    enemies.append(spawn_enemy(walls, player_tank.x, player_tank.y, game_time, level))
                    spawn_timer = 0
            heal_timer += 1
            if heal_timer > 650 and len(pickups) < 2:
                pickups.append(spawn_health(walls, player_tank.x, player_tank.y))
                heal_timer = 0
            for pickup in pickups[:]:
                if pickup.check_collision(player_tank):
                    player_tank.heal(3)
                    pickups.remove(pickup)
                else:
                    pickup.draw(screen)
            for enemy in enemies[:]:
                enemy_bullet = enemy.update_ai(player_tank, walls)
                if enemy_bullet:
                    bullets.append(enemy_bullet)
            for bullet in bullets[:]:
                bullet.update()
                if not bullet.active:
                    bullets.remove(bullet)
                    continue
                if any(wall.check_collision(bullet) for wall in walls):
                    bullet.active = False
                    continue
                if bullet.owner != player_tank:
                    if math.hypot(bullet.x - player_tank.x, bullet.y - player_tank.y) < player_tank.radius:
                        bullet.active = False
                        if player_tank.take_damage():
                            game_over = True
                else:
                    for enemy in enemies[:]:
                        if math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < enemy.radius:
                            bullet.active = False
                            score += enemy.points
                            enemies.remove(enemy)
                            break
                bullet.draw(screen)
            for wall in walls:
                wall.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            player_tank.draw(screen)
            draw_text(f"Score: {score}", 20, 20, WHITE, SMALL_FONT, center=False)
            draw_text(f"Level: {level}", WIDTH - 140, 20, YELLOW, SMALL_FONT, center=False)
        else:
            if engine_sound and engine_playing:
                engine_sound.stop()
            draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 60, RED)
            draw_text(f"Your Score: {score}", WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text("Press ESC to return", WIDTH // 2, HEIGHT // 2 + 80, WHITE, SMALL_FONT)
        pygame.display.flip()
def main_menu():
    player_name = "Player"
    btn_w = 270
    btn_h = 50
    btn_x = (WIDTH - btn_w) // 2
    buttons = [
        {"text": "New Game", "y": 220, "color": BUTTON_GREEN, "hover": BUTTON_GREEN_HOVER, "action": "new"},
        {"text": "High Score", "y": 290, "color": BUTTON_GRAY, "hover": BUTTON_GRAY_HOVER, "action": "hs"},
        {"text": "Change Name", "y": 360, "color": BUTTON_GRAY, "hover": BUTTON_GRAY_HOVER, "action": "name"},
        {"text": "Game Rules", "y": 430, "color": BUTTON_GRAY, "hover": BUTTON_GRAY_HOVER, "action": "rules"},
        {"text": "Exit", "y": 500, "color": BUTTON_RED, "hover": BUTTON_RED_HOVER, "action": "exit"}
    ]
    while True:
        if menu_background:
            screen.blit(menu_background, (0, 0))
        else:
            screen.fill(LIGHT_GRAY)
        draw_text("TANK BATTLE", WIDTH // 2, 90, WHITE, FONT)
        draw_text(f"Player: {player_name}", WIDTH // 2, 150, WHITE, SMALL_FONT)
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
        for btn in buttons:
            rect = pygame.Rect(btn_x, btn["y"], btn_w, btn_h)
            hover = rect.collidepoint(mx, my)
            draw_button(btn_x, btn["y"], btn_w, btn_h, btn["text"], btn["color"], btn["hover"], hover)
            if hover and clicked:
                if btn["action"] == "new":
                    final_score = game_loop(player_name)
                    show_result_screen(final_score, player_name)
                elif btn["action"] == "hs":
                    show_highscore_screen()
                elif btn["action"] == "name":
                    player_name = input_name_screen()
                elif btn["action"] == "rules":
                    show_rules_screen()
                elif btn["action"] == "exit":
                    pygame.quit()
                    exit()
        pygame.display.flip()
        clock.tick(FPS)
if __name__ == "__main__":
    main_menu()