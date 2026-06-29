import pygame
import math
import random
import json
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")
clock = pygame.time.Clock()
FPS = 60

GREEN       = pygame.Color('darkgreen')  
GRAY        = pygame.Color('dimgray')    
DARK_GRAY   = pygame.Color('gray25')       
BLACK       = pygame.Color('black')        
WALL_COLOR  = pygame.Color('saddlebrown')  
WALL_BORDER = pygame.Color('sienna')       
ENEMY_COLOR = pygame.Color('firebrick')  
ENEMY_DARK  = pygame.Color('darkred')      
RED         = pygame.Color('red')         
GREEN_HP    = pygame.Color('limegreen')    
BLUE        = pygame.Color('dodgerblue')   
WHITE       = pygame.Color('white')        
YELLOW      = pygame.Color('gold')   

FONT = pygame.font.Font(None, 48)
SMALL_FONT = pygame.font.Font(None, 32)
HIGH_SCORE_FILE = "highscore.json"

try:
    engine_sound = pygame.mixer.Sound(r"D:\Kriss\Work\tank_battle\engine stand.wav")
    engine_sound.set_volume(0.3)
    shot_sound = pygame.mixer.Sound(r"D:\Kriss\Work\tank_battle\semiautorifle3.wav")
    shot_sound.set_volume(0.4)
    print("Sounds loaded successfully!!")
except Exception as e:
    print(f"Error loading sounds: {e}")
    print("The game will run without sound effects")
    engine_sound = None
    shot_sound = None

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE,"r") as f:
                return json.load(f)
        except:
            return {"name":"---","score": 0}
    return {"name":"---","score": 0}

def save_high_score(name, score):
    data = {"name": name,"score": score}
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(data, f)

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

    def check_wall_collision(self, wall):
        return wall.rect.collidepoint(self.x, self.y)

class Wall:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, WALL_COLOR, self.rect)
        pygame.draw.rect(surface, WALL_BORDER, self.rect, 3)

    def check_collision(self, tank):
        tank_rect = pygame.Rect(tank.x - tank.radius, tank.y - tank.radius, tank.radius * 2, tank.radius * 2)
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
        dx = self.x - tank.x
        dy = self.y - tank.y
        return math.hypot(dx, dy) < tank.radius + self.radius

class Tank:
    def __init__(self, x, y, size="medium"):
        self.x = x
        self.y = y
        self.body_angle = 0
        self.turret_angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 4
        self.acceleration = 0.2
        self.deceleration = 0.1
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
        original_x = self.x
        original_y = self.y
        if up:
            self.speed_y = max(self.speed_y - self.acceleration, -self.max_speed)
        if down:
            self.speed_y = min(self.speed_y + self.acceleration, self.max_speed)
        if left:
            self.speed_x = max(self.speed_x - self.acceleration, -self.max_speed)
        if right:
            self.speed_x = min(self.speed_x + self.acceleration, self.max_speed)

        if not up and not down:
            if self.speed_y > 0:
                self.speed_y = max(0, self.speed_y - self.deceleration)
            elif self.speed_y < 0:
                self.speed_y = min(0, self.speed_y + self.deceleration)
        if not left and not right:
            if self.speed_x > 0:
                self.speed_x = max(0, self.speed_x - self.deceleration)
            elif self.speed_x < 0:
                self.speed_x = min(0, self.speed_x + self.deceleration)

        self.x += self.speed_x
        self.y += self.speed_y

        collision = False
        for wall in walls:
            if wall.check_collision(self):
                collision = True
                break
        if collision:
            self.x = original_x
            self.y = original_y
            self.speed_x *= 0.3
            self.speed_y *= 0.3

        speed = math.hypot(self.speed_x, self.speed_y)
        self.is_moving = speed > 0.2

        if abs(self.speed_x) > 0.1 or abs(self.speed_y) > 0.1:
            self.body_angle = math.degrees(math.atan2(-self.speed_y, self.speed_x))
            self.turret_angle = self.body_angle

        if abs(self.speed_x) > 0.2 or abs(self.speed_y) > 0.2:
            self.track_offset += self.track_speed
            if self.track_offset >= 16:
                self.track_offset = 0

        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def rotate_turret(self, direction):
        self.turret_angle += direction * 3

    def shoot(self):
        rad = math.radians(self.turret_angle)
        bullet_x = self.x + math.cos(rad) * (self.height / 2 + 8)
        bullet_y = self.y - math.sin(rad) * (self.height / 2 + 8)
        if shot_sound:
            try:
                shot_sound.play()
            except:
                pass
        return Bullet(bullet_x, bullet_y, self.turret_angle, owner=self)

    def draw(self, surface):
        rad_body = math.radians(self.body_angle)
        rad_turret = math.radians(self.turret_angle)
        body_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(body_surface, self.color, (0, 0, self.width, self.height), border_radius=6)
        pygame.draw.rect(body_surface, self.dark_color, (0, 2, 4, self.height - 4))
        pygame.draw.rect(body_surface, self.dark_color, (self.width - 4, 2, 4, self.height - 4))
        for i in range(4):
            y_pos = 6 + i * 10 + self.track_offset
            if y_pos < self.height - 6:
                pygame.draw.rect(body_surface, BLACK, (1, y_pos, 2, 4))
                pygame.draw.rect(body_surface, BLACK, (self.width - 3, y_pos, 2, 4))
        rotated_body = pygame.transform.rotate(body_surface, self.body_angle)
        rect = rotated_body.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_body, rect.topleft)

        turret_surface = pygame.Surface((self.width // 1.5, self.width // 1.5), pygame.SRCALPHA)
        pygame.draw.circle(turret_surface, self.color, (self.width//3, self.width//3), self.width//3)
        pygame.draw.rect(turret_surface, BLACK, (self.width//3, 0, 6, self.height//2))
        rotated_turret = pygame.transform.rotate(turret_surface, self.turret_angle)
        turret_rect = rotated_turret.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_turret, turret_rect.topleft)

        hp_width = self.radius * 2
        hp_height = 6
        hp_x = self.x - self.radius
        hp_y = self.y - self.radius - 12
        pygame.draw.rect(surface, RED, (hp_x, hp_y, hp_width, hp_height))
        current_hp = int((self.health / self.max_health) * hp_width)
        pygame.draw.rect(surface, GREEN_HP, (hp_x, hp_y, current_hp, hp_height))

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
        self.target_x = 0
        self.target_y = 0
        # --- NEW: extra health from level ---
        self.health += extra_hp
        self.max_health += extra_hp

    def update_ai(self, player, walls):
        self.move_timer += 1
        if self.move_timer > random.randint(80, 180):
            self.target_x = random.randint(100, WIDTH - 100)
            self.target_y = random.randint(100, HEIGHT - 100)
            self.move_timer = 0

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 10:
            angle = math.degrees(math.atan2(-dy, dx))
            diff = (angle - self.body_angle + 180) % 360 - 180
            if abs(diff) > 8:
                if diff > 0:
                    self.body_angle += 2
                else:
                    self.body_angle -= 2
            else:
                self.speed_x = math.cos(math.radians(self.body_angle)) * self.max_speed * 0.3
                self.speed_y = -math.sin(math.radians(self.body_angle)) * self.max_speed * 0.3
        else:
            self.speed_x *= 0.95
            self.speed_y *= 0.95

        dx_turret = player.x - self.x
        dy_turret = player.y - self.y
        self.turret_angle = math.degrees(math.atan2(-dy_turret, dx_turret))

        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and math.hypot(dx_turret, dy_turret) < 750:
            self.shoot_cooldown = random.randint(120, 200)
            return self.shoot()

        self.x += self.speed_x
        self.y += self.speed_y

        collision = False
        for wall in walls:
            if wall.check_collision(self):
                collision = True
                break
        if collision:
            self.x -= self.speed_x
            self.y -= self.speed_y
            self.speed_x *= -0.5
            self.speed_y *= -0.5

        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

def create_walls(count, tank_x, tank_y, safe_dist):
    walls = []
    margin = 80
    min_gap = 70
    for _ in range(count):
        while True:
            w = random.randint(50, 160)
            h = random.randint(25, 70)
            x = random.randint(margin, WIDTH - w - margin)
            y = random.randint(margin, HEIGHT - h - margin)
            center_x = x + w / 2
            center_y = y + h / 2
            dist_to_player = math.hypot(center_x - tank_x, center_y - tank_y)
            if dist_to_player < safe_dist + max(w, h) / 2 + 20:
                continue
            overlap = False
            for wall in walls:
                existing_cx = wall.x + wall.w / 2
                existing_cy = wall.y + wall.h / 2
                dist_between = math.hypot(center_x - existing_cx, center_y - existing_cy)
                if dist_between < (max(w, h) + max(wall.w, wall.h)) / 2 + min_gap:
                    overlap = True
                    break
            if not overlap:
                walls.append(Wall(x, y, w, h))
                break
    return walls

# --- UPDATED: pass level to spawn harder enemies ---
def spawn_enemy(walls, player_x, player_y, game_time, level):
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(50, WIDTH - 50)
        y = -50
    elif side == "bottom":
        x = random.randint(50, WIDTH - 50)
        y = HEIGHT + 50
    elif side == "left":
        x = -50
        y = random.randint(50, HEIGHT - 50)
    else:
        x = WIDTH + 50
        y = random.randint(50, HEIGHT - 50)

    if game_time < 1500:
        size = "small"
    elif game_time < 3000:
        size = random.choice(["small", "medium"])
    else:
        size = random.choice(["small", "medium", "large"])

    # More health per level
    extra_hp = max(0, level - 1)
    return EnemyTank(x, y, size, extra_hp=extra_hp)

def spawn_health(walls, player_x, player_y):
    margin = 100
    while True:
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        dist_to_player = math.hypot(x - player_x, y - player_y)
        if dist_to_player < 150:
            continue
        collision = False
        for wall in walls:
            if wall.rect.collidepoint(x, y):
                collision = True
                break
        if not collision:
            return HealthPickup(x, y)

def draw_text(text, x, y, color=WHITE, font=FONT):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def main_menu():
    selected = 0
    player_name = "Player"
    options = ["New Game","Score & High Score",f"Name: {player_name}","Rules","Exit"]
    rules = [ "--- GAME RULES ---",
              "- Move: Arrow Keys",
              "- Rotate Turret: Q / E",
              "- Shoot: Spacebar",
              "- Small Enemy: 5 Points",
              "- Medium Enemy: 10 Points",
              "- Large Enemy: 15 Points",
              "- Blue Circles Restore Health",
              "- You can take 12 hits before losing",
              "- Difficulty increases over time",
              "- Higher levels = more & stronger enemies",
              "",
              "Press ESC to return to menu"]
    high_score_data = load_high_score()
    while True:
        screen.fill(GREEN)
        draw_text("TANK BATTLE", WIDTH//2, 80, YELLOW, pygame.font.Font(None, 72))
        options[2] = f"Name: {player_name}"
        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            draw_text(opt, WIDTH//2, 200 + i * 60, color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        return player_name
                    elif selected == 1:
                        show_scores(high_score_data)
                    elif selected == 2:
                        new_name = enter_name()
                        if new_name.strip():
                            player_name = new_name.strip()
                    elif selected == 3:
                        show_rules(rules)
                    elif selected == 4:
                        pygame.quit()
                        return None
        pygame.display.flip()
        clock.tick(FPS)

def show_scores(high_score_data):
    while True:
        screen.fill(GREEN)
        draw_text("SCORES", WIDTH//2, 100, YELLOW)
        draw_text(f"High Score: {high_score_data['score']} ({high_score_data['name']})", WIDTH//2, 220)
        draw_text("Press ESC to go back", WIDTH//2, 350)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)

def enter_name():
    name = ""
    while True:
        screen.fill(GREEN)
        draw_text("Enter Your Name:", WIDTH//2, 150, YELLOW)
        draw_text(name + "_", WIDTH//2, 250, WHITE)
        draw_text("Press ENTER when done", WIDTH//2, 350)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "Player"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode
        pygame.display.flip()
        clock.tick(FPS)

def show_rules(rules):
    while True:
        screen.fill(GREEN)
        y = 80
        for line in rules:
            draw_text(line, WIDTH//2, y, WHITE, SMALL_FONT)
            y += 35
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)

def game_loop(player_name):
    player_tank = Tank(WIDTH // 2, HEIGHT // 2)
    walls = create_walls(12, WIDTH//2, HEIGHT//2, player_tank.radius + 30)
    enemies = []
    bullets = []
    pickups = []
    game_over = False
    running = True
    level = 1
    next_level_time = 600  
    max_enemies = 1         
    next_spawn_timer = 0
    next_health_timer = 0
    game_time = 0
    score = 0
    high_score_data = load_high_score()
    engine_playing = False
    while running:
        clock.tick(FPS)
        screen.fill(GREEN)
        game_time += 1
        if game_time >= next_level_time:
            level += 1
            next_level_time += 600
            max_enemies = min(8, 1 + (level - 1)) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if engine_sound and engine_playing:
                        engine_sound.stop()
                    return score
                if not game_over and event.key == pygame.K_SPACE:
                    bullets.append(player_tank.shoot())
        if not game_over:
            keys = pygame.key.get_pressed()
            move_up = keys[pygame.K_UP]
            move_down = keys[pygame.K_DOWN]
            move_left = keys[pygame.K_LEFT]
            move_right = keys[pygame.K_RIGHT]
            player_tank.move(move_up, move_down, move_left, move_right, walls)
            if engine_sound:
                try:
                    if player_tank.is_moving and not engine_playing:
                        engine_sound.play(-1)
                        engine_playing = True
                    elif not player_tank.is_moving and engine_playing:
                        engine_sound.stop()
                        engine_playing = False
                except:
                    pass
            if keys[pygame.K_q]:
                player_tank.rotate_turret(1)
            if keys[pygame.K_e]:
                player_tank.rotate_turret(-1)
            if len(enemies) < max_enemies:
                next_spawn_timer += 1
                spawn_delay = max(60, 120 - level * 8)  
                if next_spawn_timer > spawn_delay:
                    enemies.append(spawn_enemy(walls, player_tank.x, player_tank.y, game_time, level))
                    next_spawn_timer = 0
            next_health_timer += 1
            if next_health_timer > 600 and len(pickups) < 2:
                pickups.append(spawn_health(walls, player_tank.x, player_tank.y))
                next_health_timer = 0
            for pickup in pickups[:]:
                if pickup.check_collision(player_tank):
                    player_tank.heal(2)
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
                hit_wall = False
                for wall in walls:
                    if bullet.check_wall_collision(wall):
                        bullet.active = False
                        hit_wall = True
                        break
                if hit_wall:
                    continue
                if bullet.owner != player_tank:
                    dx = bullet.x - player_tank.x
                    dy = bullet.y - player_tank.y
                    if math.hypot(dx, dy) < player_tank.radius:
                        bullet.active = False
                        if player_tank.take_damage():
                            game_over = True
                else:
                    for enemy in enemies[:]:
                        dx = bullet.x - enemy.x
                        dy = bullet.y - enemy.y
                        if math.hypot(dx, dy) < enemy.radius:
                            bullet.active = False
                            if enemy.take_damage():
                                score += enemy.points
                                enemies.remove(enemy)
                            break
                bullet.draw(screen)
            for wall in walls:
                wall.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            player_tank.draw(screen)
            draw_text(f"Score: {score}", 80, 25, WHITE, SMALL_FONT)
            draw_text(f"Level: {level}", WIDTH - 120, 25, YELLOW, SMALL_FONT)

        else:
            if engine_sound and engine_playing:
                engine_sound.stop()
            draw_text("GAME OVER", WIDTH//2,HEIGHT//2 - 60,RED)
            draw_text(f"Your Score: {score}",WIDTH//2,HEIGHT//2,WHITE)
            if score > high_score_data["score"]:
                draw_text("NEW HIGH SCORE!",WIDTH//2,HEIGHT//2 + 50,YELLOW)
                save_high_score(player_name, score)
            draw_text("Press ESC to return to menu", WIDTH//2,HEIGHT//2 + 110,WHITE,SMALL_FONT)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return score

        pygame.display.flip()
    return score

def main():
    while True:
        player_name = main_menu()
        if player_name is None:
            break
        game_loop(player_name)

if __name__ == "__main__":
    main()