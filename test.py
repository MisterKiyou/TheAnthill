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
            if pheromones[i, j] > 0 and random.random() < 0.1:
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
    RED = (255, 0, 0)

    # Set the grid size and cell size
    cols, rows = 100, 100
    cell_size = grid_width // cols

    # Initialize the grid, sugars, and pheromones
    grid = np.zeros((cols, rows), dtype=int)
    sugars = np.zeros((cols, rows), dtype=int)
    obstacles = np.zeros((cols, rows), dtype=int)
    pheromones = np.zeros((cols, rows), dtype=int)

    # Set the initial number of ants and sugar
    num_fourmis = 1000
    num_sucre = 3
    config = Config(cols, rows)  # Initialize the config
    fourmis = []

    # Initialize control panel buttons
    buttons = {
        "Start": pygame.Rect(grid_width + 20, 20, 160, 40),
        "Pause": pygame.Rect(grid_width + 20, 80, 160, 40),
        "Sugar": pygame.Rect(grid_width + 20, 140, 160, 40),
        "Obstacle": pygame.Rect(grid_width + 20, 200, 160, 40),
        "Quit": pygame.Rect(grid_width + 20, 260, 160, 40)
    }
    selected_button = None
    game_started = False
    game_paused = False

    # Initialize stats
    sugar_collected = 0
    start_ticks = 0

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
                            if button_name == "Start":
                                if not game_started:
                                    # Initialize ants and place sugar randomly on the grid
                                    fourmis = [Ant(cols // 2, rows // 2, config) for _ in range(num_fourmis)]
                                    start_ticks = pygame.time.get_ticks()  # Start the timer
                                    game_started = True
                            elif button_name == "Pause":
                                if game_started:
                                    game_paused = not game_paused
                            elif button_name == "Quit":
                                running = False
                            else:
                                selected_button = button_name

        if game_started and not game_paused:
            # Move the ants
            for fourmi in fourmis:
                fourmi.move(grid, pheromones, sugars, obstacles)
                if fourmi.has_sugar and (fourmi.x, fourmi.y) == (cols // 2, rows // 2):
                    sugar_collected += 1
                    fourmi.has_sugar = False

            # Decay the pheromones
            decay(pheromones)

        # Draw the grid
        for i in range(cols):
            for j in range(rows):
                if grid[i, j]:
                    color = BLACK  # Cells with sugar are displayed in green
                elif sugars[i, j]:
                    color = YELLOW  # Sugar is displayed in yellow
                elif obstacles[i, j]:
                    color = BLUE  # Obstacles are displayed in black
                else:
                    pheromone_level = pheromones[i, j]
                    color = calculate_color(pheromone_level)  # Calculate the color based on pheromone level
                pygame.draw.rect(window, color, (i * cell_size, j * cell_size, cell_size, cell_size))

        # Draw the control panel
        pygame.draw.rect(window, WHITE, (grid_width, 0, control_panel_width, grid_height))
        for button_name, button_rect in buttons.items():
            if button_name == "Start" and game_started:
                button_color = RED if game_paused else BLUE
            elif button_name == "Pause" and game_started:
                button_color = GREEN if game_paused else RED
            else:
                button_color = GREEN if selected_button == button_name else BLUE
            pygame.draw.rect(window, button_color, button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render(button_name, True, BLACK)
            window.blit(text, (button_rect.x + 10, button_rect.y + 5))

        # Draw the stats
        font = pygame.font.Font(None, 28)
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000 if game_started else 0
        stats_text = [
            f"Sucre ramené: {sugar_collected}",
            f"Temps écoulé: {elapsed_seconds}s"
        ]
        for i, line in enumerate(stats_text):
            text = font.render(line, True, BLACK)
            window.blit(text, (grid_width + 20, 320 + i * 30))

        pygame.display.flip()
        pygame.time.delay(1)

    # Quit pygame
    pygame.quit()
