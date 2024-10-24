import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import random
import neat
import multiprocessing
import matplotlib.pyplot as plt
import pickle

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
FPS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
MAX_FRAMES = 1000
MAX_GENERATIONS = 50

# Direction
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x*CELL_SIZE)) % SCREEN_WIDTH), (cur[1] + (y*CELL_SIZE)) % SCREEN_HEIGHT)
        
        # Check if snake hits the screen boundaries
        if new[0] < 0 or new[0] >= SCREEN_WIDTH or new[1] < 0 or new[1] >= SCREEN_HEIGHT:
            return False  # End game if snake hits screen boundaries
        
        if len(self.positions) > 2 and new in self.positions[2:]:
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)

# Food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * CELL_SIZE, random.randint(0, GRID_HEIGHT-1) * CELL_SIZE)

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 1)

def eval_genome(genomes, config):
    global MAX_FRAMES
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        snake = Snake()
        food = Food()
        clock = pygame.time.Clock()

        fitness = 0
        frames = 0
        while frames < MAX_FRAMES:
            frames += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # Get inputs for the neural network
            head = snake.get_head_position()
            food_pos = food.position
            x_diff = food_pos[0] - head[0]
            y_diff = food_pos[1] - head[1]
            direction_vector = (snake.direction == UP, snake.direction == DOWN, snake.direction == LEFT, snake.direction == RIGHT)

            inputs = (x_diff, y_diff, direction_vector[0], direction_vector[1], direction_vector[2], direction_vector[3])

            # Activate the neural network
            output = net.activate(inputs)

            # Determine the direction to turn based on the output of the neural network
            max_index = output.index(max(output))
            if max_index == 0:
                snake.turn(UP)
            elif max_index == 1:
                snake.turn(DOWN)
            elif max_index == 2:
                snake.turn(LEFT)
            elif max_index == 3:
                snake.turn(RIGHT)

            # Move the snake
            if not snake.move():  # Check if snake hits the screen boundaries or itself
                break

            # Check if snake eats food
            if snake.get_head_position() == food.position:
                snake.length += 1
                food.randomize_position()
                fitness += 10  # Increase fitness when snake eats food
            else:
                fitness -= 0.3  # Penalize for each move without eating food

            # Update the game display
            window.fill(WHITE)
            snake.draw(window)
            food.draw(window)
            pygame.display.update()
            clock.tick(FPS)

        genome.fitness = fitness



def run(config_path):
    # Load NEAT configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population
    p = neat.Population(config)

    # Add reporters to track progress
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Initialize variables to track statistics
    max_fitness_list = []
    mean_fitness_list = []

    # Run the evolution for a maximum of MAX_GENERATIONS
    winner = p.run(eval_genome, MAX_GENERATIONS)

    # Save the best genome
    with open('snake_best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

    # Display statistics
    print('\nBest genome:\n{!s}'.format(winner))

    # Extract statistics
    generation_statistics = stats.get_stats()

    # Plot evolution
    generations = range(1, len(generation_statistics.most_fit_genomes) + 1)
    max_fitness_list = [c.fitness for c in generation_statistics.most_fit_genomes]
    mean_fitness_list = generation_statistics.get_fitness_mean()

    plt.plot(generations, max_fitness_list, label='Max Fitness')
    plt.plot(generations, mean_fitness_list, label='Mean Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Evolution of Snake Game')
    plt.legend()
    plt.grid(True)
    plt.show()



def load_best_snake(config_path, genome_path):
    # Load NEAT configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Load the best genome
    with open(genome_path, 'rb') as f:
        genome = pickle.load(f)

    # Create the neural network
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Initialize pygame
    pygame.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game')

    # Initialize the snake and food
    snake = Snake()
    food = Food()
    clock = pygame.time.Clock()

    # Run the game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Get inputs for the neural network
        head = snake.get_head_position()
        food_pos = food.position
        x_diff = food_pos[0] - head[0]
        y_diff = food_pos[1] - head[1]
        direction_vector = (snake.direction == UP, snake.direction == DOWN, snake.direction == LEFT, snake.direction == RIGHT)

        inputs = (x_diff, y_diff, direction_vector[0], direction_vector[1], direction_vector[2], direction_vector[3])

        # Activate the neural network
        output = net.activate(inputs)

        # Determine the direction to turn based on the output of the neural network
        max_index = output.index(max(output))
        if max_index == 0:
            snake.turn(UP)
        elif max_index == 1:
            snake.turn(DOWN)
        elif max_index == 2:
            snake.turn(LEFT)
        elif max_index == 3:
            snake.turn(RIGHT)

        # Move the snake
        if not snake.move():  # Check if snake hits the screen boundaries or itself
            pygame.quit()
            return

        # Check if snake eats food
        if snake.get_head_position() == food.position:
            snake.length += 1
            food.randomize_position()

        # Update the game display
        window.fill(WHITE)
        snake.draw(window)
        food.draw(window)
        pygame.display.update()
        clock.tick(FPS)


# Main function
if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game')

    load = False

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_snake.txt') 

    if load:
        genome_path = 'snake_best_genome.pkl' 
        load_best_snake(config_path, genome_path)

    else:

        run(config_path)
        pygame.quit()

