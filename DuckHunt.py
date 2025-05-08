import pygame
import random
import time
import os
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='pygame')

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
        self.spawn_interval = 5000
        self.difficulty_timer = 0
        self.difficulty_step = 500
        self.min_spawn_interval = 400
        self.paused = False

    def start(self):
        self.run()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                self.player.shoot(event.pos, self.ducks)

    def spawn_duck(self):
        if self.paused or len(self.ducks) >= 10:
            return
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            self.ducks.append(DuckFactory.create_duck())
            self.last_spawn_time = now

    def update_difficulty(self):
        if self.paused:
            return
        now = pygame.time.get_ticks()
        if now - self.difficulty_timer >= 3000:
            if self.spawn_interval > self.min_spawn_interval:
                self.spawn_interval -= self.difficulty_step
            DuckFactory.increase_speed()
            self.difficulty_timer = now

    def update(self):
        if self.paused:
            return
        for duck in self.ducks[:]:
            duck.move()

            if duck.is_hit:
                self.ducks.remove(duck)
                self.player.score += duck.points
                if duck.restore_miss:
                    self.player.misses = max(self.player.misses - 1, 0)

            elif duck.x < -duck.rect.width or duck.y < -duck.rect.height or duck.y > SCREEN_HEIGHT:
                self.ducks.remove(duck)
                self.player.misses += 1

        if self.player.misses >= 5:
            self.game_over()

    def draw(self):
        self.screen.fill(BLUE)
        for duck in self.ducks:
            duck.draw(self.screen)
        self.ui_manager.draw_score(self.player.score)
        self.ui_manager.draw_misses(self.player.misses, 5)
        if self.paused:
            self.ui_manager.draw_paused()
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
    def __init__(self, speed_x, speed_y, image, points, restore_miss=False):
        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.image = pygame.transform.scale(image, (100, 100))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_hit = False
        self.points = points
        self.restore_miss = restore_miss

    def move(self):
        self.x -= self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class NormalDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck.png"))
        speed_x = random.choice([3, 4])
        speed_y = random.choice([1, -1]) * random.randint(1, 3)
        points = 1
        super().__init__(speed_x, speed_y, image, points)


class FastDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fast.png"))
        speed_x = random.choice([6, 7])
        speed_y = random.choice([1, -1]) * random.randint(1, 3)
        points = 2
        super().__init__(speed_x, speed_y, image, points)


class FakeDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fake.png"))
        speed_x = random.choice([2, 3])
        speed_y = random.choice([1, -1]) * random.randint(1, 3)
        points = -1
        super().__init__(speed_x, speed_y, image, points)


class BonusDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_bonus.png"))
        speed_x = random.choice([3, 4])
        speed_y = random.choice([1, -1]) * random.randint(1, 3)
        points = 3
        restore_miss = True
        super().__init__(speed_x, speed_y, image, points, restore_miss)


class DuckFactory:
    speed_increase = 0

    @staticmethod
    def create_duck():
        duck_type = random.choices([NormalDuck, FastDuck, FakeDuck, BonusDuck], weights=[0.5, 0.3, 0.1, 0.1])[0]
        return duck_type()

    @staticmethod
    def increase_speed():
        DuckFactory.speed_increase += 0.5


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

    def draw_paused(self):
        paused_text = font.render("Paused", True, BLACK)
        self.screen.blit(paused_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 50))


game = Game(screen)
game.start()
pygame.quit()
