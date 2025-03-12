import pygame
import sys
pygame.init()
# Larger window
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 7  # Underlying 7x7 grid
CELL_SIZE = WIDTH // BOARD_SIZE
# Colors
BG_COLOR = (210, 180, 140)  # Tan background
LINE_COLOR = (101, 67, 33)  # Brown for connecting lines
DOT_COLOR = (0, 0, 0)  # Black for board points
# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fox and Geese Board")

def is_valid_point(row, col):
    """
    Returns True if (row, col) is part of the plus-shaped board.
    Valid if the row is 2, 3, or 4 OR the col is 2, 3, or 4.
    """
    return row in [2, 3, 4] or col in [2, 3, 4]

def is_central_point(row, col):
    """
    Returns True if the point is within the central 3x3 region.
    """
    return row in [2, 3, 4] and col in [2, 3, 4]

def draw_board():
    screen.fill(BG_COLOR)
    
    # First, draw all the orthogonal connections (horizontal and vertical lines)
    # Directions for orthogonal connections: right, down
    orthogonal_directions = [(0, 1), (1, 0)]
    
    # Draw orthogonal connecting lines
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if is_valid_point(row, col):
                center_x = col * CELL_SIZE + CELL_SIZE // 2
                center_y = row * CELL_SIZE + CELL_SIZE // 2
                
                for dr, dc in orthogonal_directions:
                    n_row = row + dr
                    n_col = col + dc
                    if 0 <= n_row < BOARD_SIZE and 0 <= n_col < BOARD_SIZE:
                        if is_valid_point(n_row, n_col):
                            neighbor_x = n_col * CELL_SIZE + CELL_SIZE // 2
                            neighbor_y = n_row * CELL_SIZE + CELL_SIZE // 2
                            pygame.draw.line(screen, LINE_COLOR, (center_x, center_y), (neighbor_x, neighbor_y), 3)
    
    # Now, add the diagonal connections
    # Each valid square should have one diagonal
    # A square is defined by its top-left corner coordinates
    
    # First identify all valid squares in the plus shape
    valid_squares = []
    for row in range(BOARD_SIZE - 1):
        for col in range(BOARD_SIZE - 1):
            # A square is valid if all four corners are valid points
            if (is_valid_point(row, col) and is_valid_point(row, col+1) and
                is_valid_point(row+1, col) and is_valid_point(row+1, col+1)):
                valid_squares.append((row, col))
    
    # Now draw a diagonal in each valid square
    # Alternate the diagonal direction for aesthetic reasons
    for i, (row, col) in enumerate(valid_squares):
        top_left_x = col * CELL_SIZE + CELL_SIZE // 2
        top_left_y = row * CELL_SIZE + CELL_SIZE // 2
        
        top_right_x = (col + 1) * CELL_SIZE + CELL_SIZE // 2
        top_right_y = row * CELL_SIZE + CELL_SIZE // 2
        
        bottom_left_x = col * CELL_SIZE + CELL_SIZE // 2
        bottom_left_y = (row + 1) * CELL_SIZE + CELL_SIZE // 2
        
        bottom_right_x = (col + 1) * CELL_SIZE + CELL_SIZE // 2
        bottom_right_y = (row + 1) * CELL_SIZE + CELL_SIZE // 2
        
        # Alternate diagonal directions based on position
        if (row + col) % 2 == 0:
            # Top-left to bottom-right diagonal
            pygame.draw.line(screen, LINE_COLOR, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 3)
        else:
            # Top-right to bottom-left diagonal
            pygame.draw.line(screen, LINE_COLOR, (top_right_x, top_right_y), (bottom_left_x, bottom_left_y), 3)
    
    # Draw the valid board points as small circles
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if is_valid_point(row, col):
                center_x = col * CELL_SIZE + CELL_SIZE // 2
                center_y = row * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, DOT_COLOR, (center_x, center_y), 6)
                
    pygame.display.flip()

# Main loop to display the board
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    draw_board()

pygame.quit()
sys.exit()