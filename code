import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 7  # 7x7 grid for traditional Fox and Geese
CELL_SIZE = WIDTH // BOARD_SIZE
LINE_WIDTH = 2
PIECE_RADIUS = CELL_SIZE // 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOARD_COLOR = (210, 180, 140)  # Tan
LINE_COLOR = (101, 67, 33)  # Brown
FOX_COLOR = (255, 69, 0)  # Red-orange
GEESE_COLOR = (220, 220, 220)  # Light gray
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fox and Geese")

# Game state
class GameState:
    def __init__(self):
        # Initialize the board positions
        # 0 = empty, 1 = fox, 2 = goose
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Set up initial positions
        # Fox at the center
        self.fox_pos = (3, 3)
        self.board[3][3] = 1
        
        # Geese in top 2 rows
        self.geese_positions = []
        for row in range(2):
            for col in range(BOARD_SIZE):
                if (row % 2 == 0 and col % 2 == 0) or (row % 2 == 1 and col % 2 == 1):
                    self.board[row][col] = 2
                    self.geese_positions.append((row, col))
        
        # Game state
        self.fox_turn = True
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
    
    def select_piece(self, row, col):
        if self.game_over:
            return
        
        # If fox's turn, can only select fox
        if self.fox_turn and self.board[row][col] == 1:
            self.selected_piece = (row, col)
            self.calculate_valid_moves()
            return True
        
        # If geese turn, can only select goose
        elif not self.fox_turn and self.board[row][col] == 2:
            self.selected_piece = (row, col)
            self.calculate_valid_moves()
            return True
        
        return False
    
    def calculate_valid_moves(self):
        self.valid_moves = []
        if not self.selected_piece:
            return
        
        row, col = self.selected_piece
        
        # Fox can move diagonally or orthogonally and can capture
        if self.fox_turn:
            # Check all 8 directions
            directions = [
                (-1, 0), (1, 0), (0, -1), (0, 1),  # orthogonal
                (-1, -1), (-1, 1), (1, -1), (1, 1)  # diagonal
            ]
            
            for dr, dc in directions:
                # Regular move
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == 0:
                    self.valid_moves.append((new_row, new_col, None))
                
                # Capture move
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == 2:
                    jump_row, jump_col = new_row + dr, new_col + dc
                    if 0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE and self.board[jump_row][jump_col] == 0:
                        self.valid_moves.append((jump_row, jump_col, (new_row, new_col)))
        
        # Geese can only move forward or sideways (not backward)
        else:
            # Geese can only move orthogonally
            directions = [(-1, 0), (0, -1), (0, 1)]  # up, left, right (no down)
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == 0:
                    self.valid_moves.append((new_row, new_col, None))
    
    def move_piece(self, row, col):
        if not self.selected_piece or (row, col) not in [move[:2] for move in self.valid_moves]:
            return False
        
        # Find the complete move information
        move_info = None
        for move in self.valid_moves:
            if move[0] == row and move[1] == col:
                move_info = move
                break
        
        if not move_info:
            return False
        
        old_row, old_col = self.selected_piece
        new_row, new_col = row, col
        capture_pos = move_info[2]
        
        # Update board
        piece_type = self.board[old_row][old_col]
        self.board[old_row][old_col] = 0
        self.board[new_row][new_col] = piece_type
        
        # Handle fox's move
        if self.fox_turn:
            self.fox_pos = (new_row, new_col)
            
            # Handle capture
            if capture_pos:
                cap_row, cap_col = capture_pos
                self.board[cap_row][cap_col] = 0
                self.geese_positions.remove((cap_row, cap_col))
                
                # Check win condition for fox - if fewer than 5 geese left
                if len(self.geese_positions) < 5:
                    self.game_over = True
                    self.winner = "Fox"
        
        # Handle goose's move
        else:
            # Update goose position
            self.geese_positions.remove((old_row, old_col))
            self.geese_positions.append((new_row, new_col))
            
            # Check if fox is trapped
            self.check_if_fox_trapped()
        
        # Reset selection
        self.selected_piece = None
        self.valid_moves = []
        
        # Switch turns
        self.fox_turn = not self.fox_turn
        return True
    
    def check_if_fox_trapped(self):
        # Check if fox has any valid moves left
        row, col = self.fox_pos
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Check regular move
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == 0:
                return False
            
            # Check jump move
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == 2:
                jump_row, jump_col = new_row + dr, new_col + dc
                if 0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE and self.board[jump_row][jump_col] == 0:
                    return False
        
        # If we get here, fox has no valid moves
        self.game_over = True
        self.winner = "Geese"
        return True

# Initialize game state
game_state = GameState()

def draw_board():
    # Fill background
    screen.fill(BOARD_COLOR)
    
    # Draw lines
    for i in range(BOARD_SIZE):
        # Vertical lines
        pygame.draw.line(screen, LINE_COLOR, 
                        (i * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2), 
                        (i * CELL_SIZE + CELL_SIZE // 2, HEIGHT - CELL_SIZE // 2), 
                        LINE_WIDTH)
        # Horizontal lines
        pygame.draw.line(screen, LINE_COLOR, 
                        (CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2), 
                        (WIDTH - CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2), 
                        LINE_WIDTH)
    
    # Draw diagonal lines
    pygame.draw.line(screen, LINE_COLOR, 
                    (CELL_SIZE // 2, CELL_SIZE // 2), 
                    (WIDTH - CELL_SIZE // 2, HEIGHT - CELL_SIZE // 2), 
                    LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, 
                    (WIDTH - CELL_SIZE // 2, CELL_SIZE // 2), 
                    (CELL_SIZE // 2, HEIGHT - CELL_SIZE // 2), 
                    LINE_WIDTH)

def draw_pieces():
    # Draw pieces
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            center_x = col * CELL_SIZE + CELL_SIZE // 2
            center_y = row * CELL_SIZE + CELL_SIZE // 2
            
            # Draw fox
            if game_state.board[row][col] == 1:
                pygame.draw.circle(screen, FOX_COLOR, (center_x, center_y), PIECE_RADIUS)
                pygame.draw.circle(screen, BLACK, (center_x, center_y), PIECE_RADIUS, 2)
                
                # Highlight selected fox
                if game_state.selected_piece == (row, col):
                    pygame.draw.circle(screen, HIGHLIGHT_COLOR, (center_x, center_y), PIECE_RADIUS + 4, 3)
            
            # Draw geese
            elif game_state.board[row][col] == 2:
                pygame.draw.circle(screen, GEESE_COLOR, (center_x, center_y), PIECE_RADIUS)
                pygame.draw.circle(screen, BLACK, (center_x, center_y), PIECE_RADIUS, 2)
                
                # Highlight selected goose
                if game_state.selected_piece == (row, col):
                    pygame.draw.circle(screen, HIGHLIGHT_COLOR, (center_x, center_y), PIECE_RADIUS + 4, 3)
    
    # Show valid moves
    for move in game_state.valid_moves:
        row, col = move[0], move[1]
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, (center_x, center_y), PIECE_RADIUS // 2)

def draw_game_over():
    if game_state.game_over:
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Create font
        font = pygame.font.SysFont(None, 72)
        
        # Render text
        text = font.render(f"{game_state.winner} wins!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Draw text
        screen.blit(text, text_rect)
        
        # Render restart instructions
        font_small = pygame.font.SysFont(None, 36)
        restart_text = font_small.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

def draw_turn_indicator():
    # Show whose turn it is
    font = pygame.font.SysFont(None, 30)
    turn_text = "Fox's Turn" if game_state.fox_turn else "Geese's Turn"
    color = FOX_COLOR if game_state.fox_turn else GEESE_COLOR
    text = font.render(turn_text, True, color)
    screen.blit(text, (10, 10))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_state.game_over:
                # Restart the game
                game_state = GameState()
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_state.game_over:
            # Get the position of the mouse click
            pos = pygame.mouse.get_pos()
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            
            # Check if within bounds
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                # If no piece is selected, try to select one
                if game_state.selected_piece is None:
                    game_state.select_piece(row, col)
                else:
                    # Try to move to this position
                    if not game_state.move_piece(row, col):
                        # If move failed, check if selecting a different piece
                        if (game_state.fox_turn and game_state.board[row][col] == 1) or \
                           (not game_state.fox_turn and game_state.board[row][col] == 2):
                            game_state.select_piece(row, col)
                        else:
                            # Deselect if clicking elsewhere
                            game_state.selected_piece = None
                            game_state.valid_moves = []
    
    # Draw everything
    draw_board()
    draw_pieces()
    draw_turn_indicator()
    draw_game_over()
    
    # Update the display
    pygame.display.flip()
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()