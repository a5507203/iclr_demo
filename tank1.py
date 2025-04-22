import pygame
import sys
import random
from collections import deque

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 640
GRID_SIZE = 32
ROWS = SCREEN_HEIGHT // GRID_SIZE
COLS = SCREEN_WIDTH // GRID_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (200, 200, 50)

# Map layout: W=walls, .=pellet
LEVEL = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W........W........W",
    "W.WWWW.W.W.WWWW.W.W",
    "W.WWWW.W.W.WWWW.W.W",
    "W..................W",
    "W.WWWW.WWWWWW.WWWW.W",
    "W......W....W......W",
    "WWWWWW.W WW W.WWWWWW",
    "     W.W WW W.W     ",
    "WWWWWW.WWWWWW.WWWWWW",
    "W..................W",
    "W.WWWW.W.W.WWWW.W.W",
    "W....W.... ....W....W",
    "WWWWW.WWW WW W.WWWWW",
    "W........W........W",
    "WWWWWWWWWWWWWWWWWWWW",
]
# Adjust map to COLS
LEVEL = [row.ljust(COLS, 'W') for row in LEVEL[:ROWS]]

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos)

class Pellet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(pos[0]+GRID_SIZE//2, pos[1]+GRID_SIZE//2))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = GRID_SIZE // 2

    def update(self, walls):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
        if not pygame.display.get_surface().get_rect().contains(self.rect):
            self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE-4, GRID_SIZE-4))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(pos[0]+2, pos[1]+2))
        self.grid_pos = (pos[0]//GRID_SIZE, pos[1]//GRID_SIZE)
        self.direction = (0, 0)
        self.speed = GRID_SIZE
        self.cooldown = 0

    def update(self, walls):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.direction != (0, 0):
            new_x = self.rect.x + self.direction[0] * self.speed
            new_y = self.rect.y + self.direction[1] * self.speed
            new_rect = self.rect.copy()
            new_rect.topleft = (new_x, new_y)
            # Check wall collision
            if not any(new_rect.colliderect(w.rect) for w in walls):
                self.rect = new_rect

    def shoot(self, bullets):
        if self.cooldown == 0:
            center = self.rect.center
            bullets.add(Bullet(center, self.direction if self.direction!=(0,0) else (0,-1)))
            self.cooldown = FPS // 2

class EnemyTank(Tank):
    def __init__(self, pos):
        super().__init__(pos, RED)

    def chase(self, target, walls):
        # Simple BFS pathfinding on grid
        start = (self.rect.x//GRID_SIZE, self.rect.y//GRID_SIZE)
        goal = (target.rect.x//GRID_SIZE, target.rect.y//GRID_SIZE)
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while queue:
            cell = queue.popleft()
            if cell == goal:
                break
            for d in dirs:
                nxt = (cell[0]+d[0], cell[1]+d[1])
                if 0 <= nxt[0] < COLS and 0 <= nxt[1] < ROWS and nxt not in visited:
                    # wall check
                    cell_rect = pygame.Rect(nxt[0]*GRID_SIZE, nxt[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    if not any(cell_rect.colliderect(w.rect) for w in walls):
                        visited[nxt] = cell
                        queue.append(nxt)
        # Backtrack
        if goal in visited:
            cur = goal
            while visited[cur] and visited[cur] != start:
                cur = visited[cur]
            dx = cur[0] - start[0]
            dy = cur[1] - start[1]
            self.direction = (dx, dy)
        else:
            self.direction = random.choice(dirs)

    def update(self, walls):
        super().update(walls)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tank Pac Battle")
    clock = pygame.time.Clock()

    walls = pygame.sprite.Group()
    pellets = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Build level
    for y, row in enumerate(LEVEL):
        for x, cell in enumerate(row):
            pos = (x*GRID_SIZE, y*GRID_SIZE)
            if cell == 'W':
                walls.add(Wall(pos))
            elif cell == '.':
                pellets.add(Pellet(pos))

    # Player
    player = Tank((GRID_SIZE, GRID_SIZE), GREEN)
    all_sprites = pygame.sprite.Group(walls, pellets, player)

    # Enemies
    for _ in range(4):
        ex, ey = random.choice([(1,1),(COLS-2,1),(1,ROWS-2),(COLS-2,ROWS-2)])
        enemy = EnemyTank((ex*GRID_SIZE, ey*GRID_SIZE))
        enemies.add(enemy)
        all_sprites.add(enemy)

    score = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    player.direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    player.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.direction = (1, 0)
                elif event.key == pygame.K_SPACE:
                    player.shoot(bullets)

        # Update
        player.update(walls)
        for enemy in enemies:
            enemy.chase(player, walls)
            enemy.update(walls)
        bullets.update(walls)

        # Bullet collisions
        for bullet in bullets:
            hit = pygame.sprite.spritecollideany(bullet, enemies)
            if hit:
                hit.kill()
                bullet.kill()
                score += 50

        # Pellet collisions
        eaten = pygame.sprite.spritecollide(player, pellets, dokill=True)
        score += len(eaten) * 10

        # Draw
        screen.fill(BLACK)
        walls.draw(screen)
        pellets.draw(screen)
        bullets.draw(screen)
        screen.blit(player.image, player.rect)
        enemies.draw(screen)

        # Score display
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()