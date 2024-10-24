import os
import sys
import pygame
import neat
import pickle
import matplotlib.pyplot as plt
import numpy as np

flappy_bird_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'flappy_bird_game'))
sys.path.append(flappy_bird_dir)

from flappy_bird import Bird, Pipe, WIDTH, HEIGHT, FPS

pygame.init()

FPS = 5000000
gravity = 0.25
generation = 0
score_history = []  # Store score history for plotting
best_scores = []  # Store best score of each generation
mean_scores = []  # Store mean score of each generation

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Load assets
background_img = pygame.image.load('flappy_bird_game/imgs/background.png').convert()
bird_img = pygame.image.load('flappy_bird_game/imgs/bird.png').convert_alpha()
pipe_img = pygame.image.load('flappy_bird_game/imgs/pipe.png').convert_alpha()

# Draw objects
def draw_objects(birds, pipes, score, generation):
    screen.blit(background_img, (0, 0))
    for bird in birds:
        screen.blit(bird.img, bird.rect)
    for pipe in pipes:
        screen.blit(pygame.transform.flip(pipe.img, False, True), pipe.top_rect)
        screen.blit(pipe.img, pipe.bottom_rect)
    font = pygame.font.Font(None, 36)
    gen_display = font.render(f"Generation: {generation}", True, (255, 255, 255))
    score_display = font.render(f"Score: {score}", True, (255, 255, 255))

    screen.blit(gen_display, (10, 10))
    screen.blit(score_display, (10, 40))
    pygame.display.update()

# Check collisions
def check_collision(birds, pipes):
    for bird in birds:
        if bird.rect.top <= 0 or bird.rect.bottom >= HEIGHT:
            return True
        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                return True
    return False

# Main function
def eval_genomes(genomes, config):
    global generation
    global score_history
    global best_scores
    global mean_scores

    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird())
        genome.fitness = 0
        ge.append(genome)

    pipes = [Pipe(WIDTH)]
    clock = pygame.time.Clock()
    
    # Initialize score
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].img.get_width():
                pipe_ind = 1
        else:
            # If there are no birds left, reset the game with a new generation
            print(f"Generation {generation} completed! Restarting with a new generation...")
            generation += 1
            score_history.append(score)  # Add score to history for plotting
            best_scores.append(max(score_history))  # Add best score of this generation
            mean_scores.append(np.mean(score_history))  # Add mean score of this generation
            score = 0  # Reset score
            break

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom_rect.bottom)))
            if output[0] > 0.5:
                bird.flap()

        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.img.get_width() < 0:
                pipes.remove(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIDTH))

        for x, bird in enumerate(birds):
            if bird.rect.top <= 0 or bird.rect.bottom >= HEIGHT:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_objects(birds, pipes, score, generation)
        clock.tick(FPS)

# Main function
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    winner = p.run(eval_genomes, 50)


    # Plot score history
    plt.plot(range(1, len(score_history) + 1), best_scores, label='Best')
    plt.plot(range(1, len(score_history) + 1), mean_scores, label='Mean')
    plt.xlabel('Generation')
    plt.ylabel('Score')
    plt.title('Score Evolution')
    plt.grid(True)
    plt.legend()
    plt.show()
    plt.savefig('score_evolution_flappy_bird_2.png')


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_flappy_bird.txt')
    run(config_path)
