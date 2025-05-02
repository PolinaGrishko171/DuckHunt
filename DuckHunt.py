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
        self.spawn_timer = 0

    def start(self):
        self.run()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.player.shoot(event.pos, self.ducks)

    def spawn_duck(self):
        if random.random() < 0.05:  
            self.ducks.append(Duck())

    def update(self):
        for duck in self.ducks:
            duck.move()
            if duck.is_hit:
                self.ducks.remove(duck)
                self.player.score += 1

        
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
        while self.is_running:
            self.handle_events()
            self.spawn_duck()
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
                return
        self.misses += 1



class Duck:
    def __init__(self):
        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 100)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.speed_x = random.choice([3, 4])
        self.speed_y = random.choice([1, -1]) * random.randint(1, 3)
        self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "duck.png"))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_hit = False

    def move(self):
        self.x -= self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))



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

