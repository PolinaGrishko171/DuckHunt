import pygame
import random
import sys

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Hunt")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def create_duck_surface(color, size=(60, 40)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(surface, color, surface.get_rect())
    return surface

normal_duck_img = create_duck_surface((0, 200, 0))
bonus_duck_img = create_duck_surface((0, 255, 255))
fake_duck_img = create_duck_surface((255, 0, 255))

class Duck:
    def __init__(self, image, speed):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 100)
        self.speed = speed

    def move(self):
        self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class NormalDuck(Duck):
    def __init__(self, speed):
        super().__init__(normal_duck_img, speed)
        self.points = 1
        self.bonus_ammo = 0
        self.penalty = 0

class BonusDuck(Duck):
    def __init__(self, speed):
        super().__init__(bonus_duck_img, speed)
        self.points = 3
        self.bonus_ammo = 1
        self.penalty = 0

class FakeDuck(Duck):
    def __init__(self, speed):
        super().__init__(fake_duck_img, speed)
        self.points = -2
        self.bonus_ammo = 0
        self.penalty = -5

def draw_menu():
    screen.fill((0, 100, 200))
    title = font.render("Duck Hunt", True, WHITE)
    play = font.render("Press any button to start", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
    screen.blit(play, (SCREEN_WIDTH//2 - play.get_width()//2, 300))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def game_loop():
    ducks = []
    score, ammo, start_time = 0, 5, pygame.time.get_ticks()
    spawn_delay, last_spawn = 1500, pygame.time.get_ticks()
    running = True
    duck_speed = 3
    next_difficulty_time = pygame.time.get_ticks() + 15000

    while running:
        screen.fill((135, 206, 235))
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and ammo > 0:
                click_pos = pygame.mouse.get_pos()
                hit = False
                for duck in ducks[:]:
                    if duck.is_clicked(click_pos):
                        score += duck.points
                        ammo += duck.bonus_ammo
                        ammo = max(ammo, 0)
                        score += duck.penalty
                        ducks.remove(duck)
                        hit = True
                        break
                if not hit:
                    ammo -= 1

        now = pygame.time.get_ticks()
        if now - last_spawn > spawn_delay:
            ducks.append(DuckFactory.create_duck(duck_speed))
            last_spawn = now

        for duck in ducks[:]:
            duck.move()
            duck.draw()
            if duck.rect.left > SCREEN_WIDTH:
                ducks.remove(duck)

        if now > next_difficulty_time:
            duck_speed += 0.5
            spawn_delay = max(500, spawn_delay - 100)
            next_difficulty_time += 15000

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Bullets: {ammo}", True, WHITE if ammo > 0 else RED), (10, 50))
        screen.blit(font.render(f"Time: {elapsed_time}s", True, WHITE), (10, 90))

        if ammo == 0:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(60)

def draw_game_over(score):
    screen.fill((0, 0, 0))
    game_over = font.render("Game over!", True, RED)
    final_score = font.render(f"Your score: {score}", True, WHITE)
    screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 250))
    screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, 300))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

class DuckFactory:
    @staticmethod
    def create_duck(speed):
        r = random.random()
        if r < 0.7:
            return NormalDuck(speed)
        elif r < 0.9:
            return BonusDuck(speed + 1)
        else:
            return FakeDuck(speed + 2)

draw_menu()
game_loop()
