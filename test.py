import pygame
import numpy as np
import random
from objects.Ant import Ant
from objects.Config import Config

def calculate_color(pheromone_level):
    """
    Calculate the color based on the pheromone level.
    
    Args:
        pheromone_level (int): The level of pheromones.
        
    Returns:
        tuple: The RGB color code.
    """
    if pheromone_level == 0:
        return WHITE
    elif pheromone_level <= 10:
        return (255, 255 - pheromone_level * 25, 255 - pheromone_level * 25)
    else:
        intensity = max(0, 255 - (pheromone_level - 10) * 15)
        return (intensity, 0, 0)

def decay(pheromones):
    """
    Decay the pheromones on the grid.
    
    Args:
        pheromones (numpy.ndarray): The pheromone grid.
    """
    for i in range(pheromones.shape[0]):
        for j in range(pheromones.shape[1]):
            if pheromones[i, j] > 0 and random.random() < 0.01:
                pheromones[i, j] -= 1

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    # Set the window size
    grid_width, grid_height = 800, 800
    control_panel_width = 200
    window_width = grid_width + control_panel_width
    window = pygame.display.set_mode((window_width, grid_height))
    pygame.display.set_caption("Ant Algorithm with Control Panel")

    # Define the colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Set the grid size and cell size
    cols, rows = 100, 100
    cell_size = grid_width // cols

    # Initialize the grid, sugars, and pheromones
    grid = np.zeros((cols, rows), dtype=int)
    sugars = np.zeros((cols, rows), dtype=int)
    obstacles = np.zeros((cols, rows), dtype=int)
    pheromones = np.zeros((cols, rows), dtype=int)

    # Set the number of ants and sugar
    num_fourmis = 1000
    num_sucre = 3
    config = Config(cols, rows)  # Initialize the config
    fourmis = [Ant(cols // 2, rows // 2, config) for _ in range(num_fourmis)]

    # Place sugar randomly on the grid
    for _ in range(num_sucre):
        x, y = random.randint(0, cols - 1), random.randint(0, rows - 1)
        sugars[x, y] = 1  # 1 represents sugar

    # Initialize control panel buttons
    buttons = {
        "Sugar": pygame.Rect(grid_width + 20, 20, 160, 40),
        "Obstacle": pygame.Rect(grid_width + 20, 80, 160, 40)
    }
    selected_button = None

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_x < grid_width:
                    grid_x, grid_y = mouse_x // cell_size, mouse_y // cell_size
                    if selected_button == "Sugar":
                        sugars[grid_x, grid_y] = 1
                    elif selected_button == "Obstacle":
                        obstacles[grid_x, grid_y] = 1
                else:
                    for button_name, button_rect in buttons.items():
                        if button_rect.collidepoint(mouse_x, mouse_y):
                            selected_button = button_name

        # Move the ants
        for fourmi in fourmis:
            fourmi.move(grid, pheromones, sugars, obstacles)

        # Decay the pheromones
        decay(pheromones)

        # Draw the grid
        for i in range(cols):
            for j in range(rows):
                if sugars[i, j]:
                    color = YELLOW  # Sugar is displayed in yellow
                else:
                    pheromone_level = pheromones[i, j]
                    color = calculate_color(pheromone_level) if grid[i, j] == 0 else BLACK
                pygame.draw.rect(window, color, (i * cell_size, j * cell_size, cell_size, cell_size))

        # Draw the control panel
        pygame.draw.rect(window, WHITE, (grid_width, 0, control_panel_width, grid_height))
        for button_name, button_rect in buttons.items():
            pygame.draw.rect(window, GREEN if selected_button == button_name else BLUE, button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render(button_name, True, BLACK)
            window.blit(text, (button_rect.x + 10, button_rect.y + 5))

        pygame.display.flip()
        pygame.time.delay(1)

    # Quit pygame
    pygame.quit()
