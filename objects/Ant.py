import random

# Directions possibles pour la fourmi (haut, droite, bas, gauche, haut-droite, bas-droite, haut-gauche, bas-gauche)
directions = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (-1, 1), (1, 1), (-1, -1)]

class Ant:
    """
    Class representing an Ant in the Ant Colony Optimization algorithm.
    """

    def __init__(self, x, y, config):
        """
        Initialize an Ant object.

        Args:
            x (int): initial x position
            y (int): initial y position
            config (Config): configuration object
        """
        self.x = x
        self.y = y
        self.config = config
        self.direction = 0  # Start facing up
        self.has_sugar = False
        self.is_getting_back = False
        self.path = []  # Path followed by the Ant

    def move(self, grid, pheromones, sugars, obstacles):
        """
        Move the Ant according to the Ant Colony Optimization algorithm.

        Args:
            grid (numpy.ndarray): grid representing the environment
            pheromones (numpy.ndarray): pheromone levels in the environment
            sugars (numpy.ndarray): sugar levels in the environment
        """
        if self.has_sugar:
            self.get_back_home(grid, pheromones, 1)
        elif len(self.path) > 400 or self.is_getting_back:
            self.is_getting_back = True
            self.get_back_home(grid, pheromones, 0)
        else:
            self.search(grid, pheromones, sugars, obstacles)

    def get_back_home(self, grid, pheromones, prob):
        """
        Move the Ant back to its home position.

        Args:
            grid (numpy.ndarray): grid representing the environment
            pheromones (numpy.ndarray): pheromone levels in the environment
            prob (float): probability of leaving pheromones
        """
        grid[self.x, self.y] = 0
        if self.path:
            # Move back to the previously visited position
            self.x, self.y = self.path.pop()
        else:
            self.has_sugar = False  # If the path is empty, the Ant has returned home
            self.is_getting_back = False
        grid[self.x, self.y] = 1

        # Deposit pheromones
        self.leave_trace(pheromones, prob)

    def search(self, grid, pheromones, sugars, obstacles):
        """
        Search for sugar in the environment.

        Args:
            grid (numpy.ndarray): grid representing the environment
            pheromones (numpy.ndarray): pheromone levels in the environment
            sugars (numpy.ndarray): sugar levels in the environment
            obstacles (numpy.ndarray): obstacles in the environment
        """
        self.path.append((self.x, self.y))  # Memorize current position

        # Influence by pheromones
        if random.random() < 0.1:  # 10% chance of being influenced by pheromones
            self.influence_by_pheromones(pheromones)
        else:
            # Choose randomly to turn right or left
            self.direction = (self.direction + random.choice([-1, 1])) % 4

        # Calculate new position
        new_x = (self.x + directions[self.direction][0]) % self.config.cols
        new_y = (self.y + directions[self.direction][1]) % self.config.rows

        # Check if the new position is not an obstacle
        if obstacles[new_x, new_y] == 0:
            grid[self.x, self.y] = 0  # Clear current cell
            self.x, self.y = new_x, new_y  # Move to the new cell
            grid[self.x, self.y] = 1  # Mark new cell as occupied

            # If the Ant finds sugar, it takes it
            if sugars[self.x, self.y] == 1:
                self.has_sugar = True
                # Deposit pheromones
                # self.leave_trace(pheromones)

    def leave_trace(self, pheromones, prob=1, max_pheromone=30):
        """
        Leave pheromones behind the Ant.

        Args:
            pheromones (numpy.ndarray): pheromone levels in the environment
            prob (float): probability of leaving pheromones
            max_pheromone (int): maximum pheromone level
        """
        if random.random() < prob:
            pheromones[self.x, self.y] = min(max_pheromone, pheromones[self.x, self.y] + 1)

    def influence_by_pheromones(self, pheromones):
        """
        Influence the Ant's direction by pheromones.

        Args:
            pheromones (numpy.ndarray): pheromone levels in the environment
        """
        pheromone_levels = [
            pheromones[(self.x + dx) % self.config.cols, (self.y + dy) % self.config.rows]
            for dx, dy in directions
        ]
        max_pheromones = max(pheromone_levels)
        if max_pheromones > 0:
            self.direction = pheromone_levels.index(max_pheromones)
