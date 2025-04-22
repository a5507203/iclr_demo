import pygame
import random

# Global configurations:
CELL_SIZE = 30    # Size of a single grid cell (in pixels)
COLS = 10         # Columns of grid
ROWS = 20         # Rows of grid
PLAY_WIDTH = COLS * CELL_SIZE   # 300 pixels
PLAY_HEIGHT = ROWS * CELL_SIZE  # 600 pixels

# Window size (add sidebar for next piece, score, etc.)
SIDEBAR_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

# Colors (RGB)
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GRAY    = (128, 128, 128)

# Define colors for each tetromino type.
# Colors are vibrant for clarity.
TETROMINO_COLORS = {
    'S': (0, 255, 0),       # bright green
    'Z': (255, 0, 0),       # red
    'I': (0, 255, 255),     # cyan
    'O': (255, 255, 0),     # yellow
    'J': (0, 0, 255),       # blue
    'L': (255, 165, 0),     # orange
    'T': (128, 0, 128)      # purple
}

# Tetromino shapes in their rotation states.
# Each shape is represented as a list of 4x4 grid strings.
SHAPES = {
    'S': [
        ['.....',
         '.....',
         '..00.',
         '.00..',
         '.....'],
        ['.....',
         '..0..',
         '..00.',
         '...0.',
         '.....']
    ],
    'Z': [
        ['.....',
         '.....',
         '.00..',
         '..00.',
         '.....'],
        ['.....',
         '..0..',
         '.00..',
         '.0...',
         '.....']
    ],
    'I': [
        ['..0..',
         '..0..',
         '..0..',
         '..0..',
         '.....'],
        ['.....',
         '0000.',
         '.....',
         '.....',
         '.....']
    ],
    'O': [
        ['.....',
         '.....',
         '.00..',
         '.00..',
         '.....']
    ],
    'J': [
        ['.....',
         '.0...',
         '.000.',
         '.....',
         '.....'],
        ['.....',
         '..00.',
         '..0..',
         '..0..',
         '.....'],
        ['.....',
         '.....',
         '.000.',
         '...0.',
         '.....'],
        ['.....',
         '..0..',
         '..0..',
         '.00..',
         '.....']
    ],
    'L': [
        ['.....',
         '...0.',
         '.000.',
         '.....',
         '.....'],
        ['.....',
         '..0..',
         '..0..',
         '..00.',
         '.....'],
        ['.....',
         '.....',
         '.000.',
         '.0...',
         '.....'],
        ['.....',
         '.00..',
         '..0..',
         '..0..',
         '.....']
    ],
    'T': [
        ['.....',
         '..0..',
         '.000.',
         '.....',
         '.....'],
        ['.....',
         '..0..',
         '..00.',
         '..0..',
         '.....'],
        ['.....',
         '.....',
         '.000.',
         '..0..',
         '.....'],
        ['.....',
         '..0..',
         '.00..',
         '..0..',
         '.....']
    ]
}

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x    # x coordinate on grid (column index)
        self.y = y    # y coordinate on grid (row index)
        self.shape = shape
        self.rotation = 0

    @property
    def current_shape(self):
        """Return the list of strings for current rotation state."""
        return SHAPES[self.shape][self.rotation % len(SHAPES[self.shape])]

    def get_cells(self):
        """Convert the current shape grid into board positions (x, y)."""
        cells = []
        grid_format = self.current_shape
        for i, line in enumerate(grid_format):
            for j, char in enumerate(line):
                if char == '0':
                    # The shape is defined in a 5x5 grid, adjust offsets.
                    cells.append((self.x + j - 2, self.y + i - 2))
        return cells

def create_grid(locked_positions={}):
    """
    Create a grid of [ROWS x COLS] where each cell is either BLACK (empty)
    or colored (if a tetromino has been locked there).
    """
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (j, i) in locked_positions:
        # (j, i) where j is the column and i is the row.
        grid[i][j] = locked_positions[(j, i)]
    return grid

def valid_space(tetromino, grid):
    """Return True if the tetromino's position is valid (not off-grid/colliding)."""
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == BLACK]
    formatted = tetromino.get_cells()
    for pos in formatted:
        x, y = pos
        if (x, y) not in accepted_positions:
            if y < 0:
                continue
            return False
    return True

def check_lost(locked_positions):
    """Return True if any locked position is above the screen (y < 1)."""
    for (j, i) in locked_positions:
        if i < 1:
            return True
    return False

def draw_grid(surface, grid):
    """Draw the grid lines for both rows and columns."""
    for i in range(ROWS):
        # Horizontal lines
        pygame.draw.line(surface, GRAY, (0, i * CELL_SIZE), (PLAY_WIDTH, i * CELL_SIZE))
    for j in range(COLS):
        # Vertical lines
        pygame.draw.line(surface, GRAY, (j * CELL_SIZE, 0), (j * CELL_SIZE, PLAY_HEIGHT))

def draw_window(surface, grid, score, lines_cleared, next_piece):
    """Draw the main game area, border, sidebar information (score, next piece)."""
    surface.fill(BLACK)

    # Draw game area (left panel)
    # Fill background (if desired) then grid blocks
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j],
                             (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    # Draw the border around game area
    pygame.draw.rect(surface, WHITE, (0, 0, PLAY_WIDTH, PLAY_HEIGHT), 4)

    # Sidebar Text and Next Piece:
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render("Score: " + str(score), 1, WHITE)
    surface.blit(label, (PLAY_WIDTH + 20, 30))

    label2 = font.render("Lines: " + str(lines_cleared), 1, WHITE)
    surface.blit(label2, (PLAY_WIDTH + 20, 70))

    label3 = font.render("Next:", 1, WHITE)
    surface.blit(label3, (PLAY_WIDTH + 20, 130))

    # Draw next piece in the sidebar.
    next_cells = next_piece.get_cells()
    # For drawing the next piece, we want a separate offset.
    offset_x = PLAY_WIDTH + 20
    offset_y = 170
    for cell in next_cells:
        # Each tetromino's grid for preview is small so adjust offset:
        x, y = cell
        # To center the piece visually, we shift the position.
        pygame.draw.rect(surface, TETROMINO_COLORS[next_piece.shape],
                         (offset_x + (x + 2) * CELL_SIZE//2, offset_y + (y + 2) * CELL_SIZE//2,
                          CELL_SIZE//2, CELL_SIZE//2), 0)

    pygame.display.update()

def clear_rows(grid, locked):
    """
    Check if any row is completely filled and clear them.
    Return: number of cleared rows.
    """
    cleared = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            cleared += 1
            # remove positions from the locked dict
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    continue
            # shift every row above down
            for key in sorted(list(locked), key=lambda x: x[1], reverse=True):
                x, y = key
                if y < i:
                    locked[(x, y + 1)] = locked.pop((x, y))
    return cleared

def get_random_tetromino():
    """Return a new Tetromino object in the top middle of grid with a random shape."""
    shape = random.choice(list(SHAPES.keys()))
    # Start roughly at the top middle (x = COLS//2)
    tetromino = Tetromino(COLS // 2, 0, shape)
    return tetromino

def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")

    locked_positions = {}  # Dict with keys as (col, row) positions and value as color.
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_random_tetromino()
    next_piece = get_random_tetromino()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # seconds per drop (can be gradually increased with score)
    score = 0
    lines_cleared = 0

    while run:
        grid = create_grid(locked_positions)
        # Increase fall_time based on clock time.
        fall_time += clock.get_rawtime()/1000.0
        clock.tick()

        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    # Rotate piece
                    current_piece.rotation = (current_piece.rotation + 1) % len(SHAPES[current_piece.shape])
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(SHAPES[current_piece.shape])

        # Update grid with current piece's position.
        for x, y in current_piece.get_cells():
            if y >= 0:
                grid[y][x] = TETROMINO_COLORS[current_piece.shape]

        # When piece must be locked into place.
        if change_piece:
            for pos in current_piece.get_cells():
                x, y = pos
                if y < 0:
                    continue  # sometimes positions above the visible grid
                locked_positions[(x, y)] = TETROMINO_COLORS[current_piece.shape]
            # Create new piece.
            current_piece = next_piece
            next_piece = get_random_tetromino()
            change_piece = False
            # Clear rows if filled.
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                lines_cleared += cleared
                # Increase score (example scoring formula)
                score += (cleared ** 2) * 100

        draw_window(win, grid, score, lines_cleared, next_piece)

        # Check for game over.
        if check_lost(locked_positions):
            font = pygame.font.SysFont('comicsans', 60)
            label = font.render("GAME OVER", 1, WHITE)
            win.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, PLAY_HEIGHT // 2 - label.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

    pygame.quit()

if __name__ == '__main__':
    main()
