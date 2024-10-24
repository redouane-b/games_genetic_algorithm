import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 288, 512
FPS = 60
gravity = 0.25
bird_movement = 0
score = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Load assets
background_img = pygame.image.load('flappy_bird_game/imgs/background.png').convert()
bird_img = pygame.image.load('flappy_bird_game/imgs/bird.png').convert_alpha()
pipe_img = pygame.image.load('flappy_bird_game/imgs/pipe.png').convert_alpha()

# Bird class
class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.vel = 0
        self.img = bird_img
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def flap(self):
        self.vel = -6

    def move(self):
        self.vel += gravity
        self.y += self.vel
        self.rect.centery = self.y

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(150, 350)
        self.img = pipe_img
        self.top_rect = self.img.get_rect(topleft=(self.x, self.y - 320))
        self.bottom_rect = self.img.get_rect(topleft=(self.x, self.y + 150))
        self.passed = False
        self.height = self.y  # Added height attribute

    def move(self):
        self.x -= 2
        self.top_rect.left = self.x
        self.bottom_rect.left = self.x

    def collide(self, bird):
        if bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect):
            return True
        return False

# Draw objects
def draw_objects(bird, pipes, score):
    screen.blit(background_img, (0, 0))
    screen.blit(bird.img, bird.rect)
    for pipe in pipes:
        screen.blit(pygame.transform.flip(pipe.img, False, True), pipe.top_rect)
        screen.blit(pipe.img, pipe.bottom_rect)
    font = pygame.font.Font(None, 36)
    score_display = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_display, (10, 10))
    pygame.display.update()

# Check collisions
def check_collision(bird, pipes):
    if bird.rect.top <= 0 or bird.rect.bottom >= HEIGHT:
        return True
    for pipe in pipes:
        if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
            return True
    return False

# Main function
def main():
    global bird_movement, score
    bird = Bird()
    pipes = [Pipe(WIDTH)]
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.flap()  # Bird flaps when mouse button is pressed

        bird.move()
        bird_movement += 1

        if bird_movement % 90 == 0:
            pipes.append(Pipe(WIDTH))
        # Check if bird passed through a pipe
        for pipe in pipes:
            if pipe.x == bird.x:
                score += 1

        for pipe in pipes:
            pipe.move()
            if pipe.x + pipe.img.get_width() < 0:
                pipes.remove(pipe)

        if check_collision(bird, pipes):
            print(f"Game Over! Final Score: {score}") 
            pygame.quit()
            sys.exit()

        draw_objects(bird, pipes, score)
        clock.tick(FPS)

if __name__ == "__main__":
    main()
