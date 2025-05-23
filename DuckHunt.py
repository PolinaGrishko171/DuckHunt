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
        self.max_bullets = 5
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.pause_start = None

    def start(self):
        self.run()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.toggle_pause()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.paused:
                if self.player.bullets > 0:
                    hit = self.player.shoot(event.pos, self.ducks)
                    if not hit:
                        self.player.bullets -= 1

    def toggle_pause(self):
        self.paused = not self.paused
        now = pygame.time.get_ticks()
        if self.paused:
            self.pause_start = now
        elif self.pause_start:
            self.paused_time += now - self.pause_start
            self.pause_start = None

    def get_elapsed_time(self):
        paused_duration = pygame.time.get_ticks() - self.pause_start if self.paused and self.pause_start else 0
        return (pygame.time.get_ticks() - self.start_time - self.paused_time - paused_duration) // 1000

    def spawn_duck(self):
        if self.paused or len(self.ducks) >= 10:
            return
        if pygame.time.get_ticks() - self.last_spawn_time >= self.spawn_interval:
            self.ducks.append(DuckFactory.create_duck())
            self.last_spawn_time = pygame.time.get_ticks()

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
                    self.player.bullets = min(self.player.bullets + 1, self.max_bullets)
            elif duck.x < -duck.rect.width or duck.y < -duck.rect.height or duck.y > SCREEN_HEIGHT:
                self.ducks.remove(duck)

        if self.player.bullets <= 0:
            self.game_over()

    def draw(self):
        self.screen.fill(BLUE)
        for duck in self.ducks:
            duck.draw(self.screen)
        self.ui_manager.draw_score(self.player.score)
        self.ui_manager.draw_bullets(self.player.bullets)
        self.ui_manager.draw_timer(self.get_elapsed_time())
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
        self.bullets = 5

    def shoot(self, position, ducks):
        for duck in ducks:
            if duck.rect.collidepoint(position):
                duck.is_hit = True
                self.score += duck.points
                if duck.restore_miss:
                    self.bullets = min(self.bullets + 1, 5)
                return True
        return False


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
        super().__init__(random.choice([3, 4]), random.choice([1, -1]) * random.randint(1, 3), image, points=1)


class FastDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fast.png"))
        super().__init__(random.choice([6, 7]), random.choice([1, -1]) * random.randint(1, 3), image, points=2)


class FakeDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_fake.png"))
        super().__init__(random.choice([2, 3]), random.choice([1, -1]) * random.randint(1, 3), image, points=-1)


class BonusDuck(Duck):
    def __init__(self):
        image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck_bonus.png"))
        super().__init__(random.choice([3, 4]), random.choice([1, -1]) * random.randint(1, 3), image, points=3, restore_miss=True)


class DuckFactory:
    speed_increase = 0

    @staticmethod
    def create_duck():
        return random.choices([NormalDuck, FastDuck, FakeDuck, BonusDuck], weights=[0.5, 0.3, 0.1, 0.1])[0]()

    @staticmethod
    def increase_speed():
        DuckFactory.speed_increase += 0.5


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.bullet_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "bullet.png"))
        self.bullet_image = pygame.transform.scale(self.bullet_image, (32, 32))

    def draw_score(self, score):
        text = font.render(f"Score: {score}", True, BLACK)
        self.screen.blit(text, (10, 10))

    def draw_bullets(self, bullets):
        for i in range(bullets):
            self.screen.blit(self.bullet_image, (10 + i * 40, 50))

    def draw_gameover(self):
        text = font.render("Game Over", True, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

    def draw_paused(self):
        text = font.render("Paused", True, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 50))

    def draw_button(self, text, x, y, width, height):
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height))
        self.screen.blit(font.render(text, True, BLACK), (x + 10, y + 10))

    def draw_menu(self):
        self.screen.fill(BLUE)
        self.draw_button("Start Game", 300, 250, 200, 50)
        self.draw_button("Exit", 300, 350, 200, 50)
        pygame.display.flip()

    def draw_timer(self, seconds):
        text = font.render(f"Time: {seconds}s", True, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH - 150, 10))


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.ui_manager = UIManager(screen)
        self.is_running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 300 <= x <= 500:
                    if 250 <= y <= 300:
                        return "start"
                    elif 350 <= y <= 400:
                        return "exit"
        return None

    def run(self):
        while self.is_running:
            self.ui_manager.draw_menu()
            action = self.handle_events()
            if action:
                return action


def main():
    menu = Menu(screen)
    action = menu.run()

    if action == "start":
        game = Game(screen)
        game.start()
    pygame.quit()


if __name__ == "__main__":
    main()
