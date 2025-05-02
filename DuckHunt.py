import pygame
import random
import time
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Hunt")

WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 36)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.ducks = []
        self.ui_manager = UIManager(screen)
        self.is_running = True
        self.last_spawn_time = 0
        self.spawn_interval = 2000
        self.difficulty_timer = 0
        self.difficulty_step = 500
        self.min_spawn_interval = 400

    def start(self):
        self.run()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.player.shoot(event.pos, self.ducks)

    def spawn_duck(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            self.ducks.append(Duck())
            self.last_spawn_time = now

    def update_difficulty(self):
        now = pygame.time.get_ticks()
        if now - self.difficulty_timer >= 3000:
            if self.spawn_interval > self.min_spawn_interval:
                self.spawn_interval -= self.difficulty_step
            Duck.increase_speed()
            self.difficulty_timer = now

    def update(self):
        for duck in self.ducks[:]:
            duck.move()
            if duck.is_hit:
                self.ducks.remove(duck)
                self.player.score += duck.points

        self.ducks = [duck for duck in self.ducks if 0 <= duck.x <= SCREEN_WIDTH]

        if self.player.misses >= 5:
            self.game_over()

    def draw(self):
        self.screen.fill(BLUE)
        for duck in self.ducks:
            duck.draw(self.screen)
        self.ui_manager.draw_score(self.player.score)
        self.ui_manager.draw_misses(self.player.misses, 5)
        pygame.display.flip()

    def game_over(self):
        self.ui_manager.draw_gameover()
        pygame.display.flip()
        time.sleep(2)
        self.is_running = False

    def run(self):
        self.difficulty_timer = pygame.time.get_ticks()
        while self.is_running:
            self.handle_events()
            self.spawn_duck()
            self.update_difficulty()
            self.update()
            self.draw()
            self.clock.tick(60)


class Player:
    def __init__(self):
        self.score = 0
        self.misses = 0

    def shoot(self, position, ducks):
        for duck in ducks:
            if duck.rect.collidepoint(position):
                duck.is_hit = True
                self.score += duck.points
                return
        self.misses += 1


class Duck:
    speed_increase = 0

    def __init__(self):
        self.type = random.choices(['normal', 'fast', 'fake'], weights=[0.6, 0.3, 0.1])[0]

        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)

        if self.type == 'normal':
            self.speed_x = random.choice([3, 4])
            self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck.png"))
            self.points = 1
        elif self.type == 'fast':
            self.speed_x = random.choice([6, 7])
            self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fast.png"))
            self.points = 2
        elif self.type == 'fake':
            self.speed_x = random.choice([2, 3])
            self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fake.png"))
            self.points = -1  

        self.speed_y = random.choice([1, -1]) * random.randint(1, 3)
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_hit = False

    def move(self):
        self.x -= self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    @classmethod
    def increase_speed(cls):
        cls.speed_increase += 0.5


class UIManager:
    def __init__(self, screen):
        self.screen = screen

    def draw_score(self, score):
        score_text = font.render(f"Score: {score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

    def draw_misses(self, misses, max_misses):
        misses_text = font.render(f"Misses: {misses}/{max_misses}", True, BLACK)
        self.screen.blit(misses_text, (10, 40))

    def draw_gameover(self):
        gameover_text = font.render("Game Over", True, BLACK)
        self.screen.blit(gameover_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))


game = Game(screen)
game.start()
pygame.quit()
