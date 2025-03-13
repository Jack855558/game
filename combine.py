import pygame
import sys

pygame.init()

# Window and board settings
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 7  # 7x7 grid underlying the plus-shaped board
CELL_SIZE = WIDTH // BOARD_SIZE

# Colors
BG_COLOR = (210, 180, 140)     # Tan background
LINE_COLOR = (101, 67, 33)     # Brown for connecting lines
DOT_COLOR = (0, 0, 0)          # Black for board points
FOX_COLOR = (255, 69, 0)       # Red-orange for fox
GEESE_COLOR = (220, 220, 220)  # Light gray for geese
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlights
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

##########################################################################
# Board definition: A cell is valid if its row or column is in [2, 3, 4].
##########################################################################
def is_valid_point(row, col):
    return (row in [2, 3, 4]) or (col in [2, 3, 4])

# Create a dictionary to store which diagonals exist
diagonal_connections = {}

def initialize_diagonal_connections():
    """Create a mapping of all valid diagonal connections on the board"""
    global diagonal_connections
    diagonal_connections.clear()
    
    # Identify squares where all four corners are valid points
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            if (is_valid_point(r, c) and is_valid_point(r, c+1) and
                is_valid_point(r+1, c) and is_valid_point(r+1, c+1)):
                
                # Get the four points
                tl = (r, c)       # top-left
                tr = (r, c+1)     # top-right
                bl = (r+1, c)     # bottom-left
                br = (r+1, c+1)   # bottom-right
                
                # Store connections based on the parity check used in drawing
                if (r + c) % 2 == 0:  # Diagonal from top-left to bottom-right
                    diagonal_connections[(tl, br)] = True
                    diagonal_connections[(br, tl)] = True
                else:  # Diagonal from top-right to bottom-left
                    diagonal_connections[(tr, bl)] = True
                    diagonal_connections[(bl, tr)] = True

def has_diagonal_connection(row, col, dr, dc):
    """
    Check if there's an actual diagonal line connection from (row, col) in direction (dr, dc).
    """
    # Calculate the target position
    target_row, target_col = row + dr, col + dc
    
    # Check if the connection exists in our diagonal_connections dictionary
    return ((row, col), (target_row, target_col)) in diagonal_connections

################################################################################
# Game state
# Geese distribution:
# - Row 4: 7 geese (columns 0..6)
# - Row 5: 3 geese (columns 2..4)
# - Row 6: 3 geese (columns 2..4)
# Fox is at (3,3) and geese move first.
################################################################################
class GameState:
    def __init__(self):
        # Create board: valid cells get 0; invalid cells are None.
        self.board = []
        for row in range(BOARD_SIZE):
            row_list = []
            for col in range(BOARD_SIZE):
                if is_valid_point(row, col):
                    row_list.append(0)
                else:
                    row_list.append(None)
            self.board.append(row_list)
        
        # Place fox at center (3,3)
        self.fox_pos = (3, 3)
        self.board[3][3] = 1

        # Place geese:
        # 7 geese on row 4 (columns 0..6)
        # 3 geese on row 5 (columns 2..4)
        # 3 geese on row 6 (columns 2..4)
        self.geese_positions = []
        for col in range(7):
            self.board[4][col] = 2
            self.geese_positions.append((4, col))
        for col in [2, 3, 4]:
            self.board[5][col] = 2
            self.geese_positions.append((5, col))
        for col in [2, 3, 4]:
            self.board[6][col] = 2
            self.geese_positions.append((6, col))
        
        # Geese move first.
        self.fox_turn = False

        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None

    def select_piece(self, row, col):
        if self.game_over or not is_valid_point(row, col):
            return False
        # Geese turn: select goose.
        if not self.fox_turn and self.board[row][col] == 2:
            self.selected_piece = (row, col)
            self.calculate_valid_moves()
            return True
        # Fox turn: select fox.
        if self.fox_turn and self.board[row][col] == 1:
            self.selected_piece = (row, col)
            self.calculate_valid_moves()
            return True
        return False

    def calculate_valid_moves(self):
        self.valid_moves = []
        if not self.selected_piece:
            return
        row, col = self.selected_piece
        piece_type = self.board[row][col]
        
        # Fox moves: all 8 directions (diagonals require connection)
        if piece_type == 1:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_r, new_c = row + dr, col + dc
                # For diagonal moves, check connection.
                if dr != 0 and dc != 0:
                    if not has_diagonal_connection(row, col, dr, dc):
                        continue
                if 0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE and is_valid_point(new_r, new_c):
                    # Normal move if destination is empty.
                    if self.board[new_r][new_c] == 0:
                        self.valid_moves.append((new_r, new_c, None))
                    # Capture move: if adjacent cell has a goose.
                    elif self.board[new_r][new_c] == 2:
                        jump_r, jump_c = new_r + dr, new_c + dc
                        if 0 <= jump_r < BOARD_SIZE and 0 <= jump_c < BOARD_SIZE and is_valid_point(jump_r, jump_c) and self.board[jump_r][jump_c] == 0:
                            if dr != 0 and dc != 0:
                                # For diagonal capture, check both steps.
                                if not (has_diagonal_connection(row, col, dr, dc) and has_diagonal_connection(new_r, new_c, dr, dc)):
                                    continue
                            self.valid_moves.append((jump_r, jump_c, (new_r, new_c)))
        # Geese moves: now include diagonal upward moves if a connection exists.
        elif piece_type == 2:
            # Allow up, left, right plus upward diagonals.
            directions = [(-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
            for dr, dc in directions:
                new_r, new_c = row + dr, col + dc
                # For diagonal moves, check connection.
                if dr != 0 and dc != 0:
                    if not has_diagonal_connection(row, col, dr, dc):
                        continue
                if 0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE:
                    if is_valid_point(new_r, new_c) and self.board[new_r][new_c] == 0:
                        self.valid_moves.append((new_r, new_c, None))
    
    def move_piece(self, row, col):
        if not self.selected_piece or (row, col) not in [(m[0], m[1]) for m in self.valid_moves]:
            return False
        old_r, old_c = self.selected_piece
        piece_type = self.board[old_r][old_c]
        capture_pos = None
        for mv in self.valid_moves:
            if (mv[0], mv[1]) == (row, col):
                capture_pos = mv[2]
                break
        
        self.board[old_r][old_c] = 0
        self.board[row][col] = piece_type
        
        if piece_type == 1:
            self.fox_pos = (row, col)
            if capture_pos:
                cap_r, cap_c = capture_pos
                self.board[cap_r][cap_c] = 0
                if (cap_r, cap_c) in self.geese_positions:
                    self.geese_positions.remove((cap_r, cap_c))
                if len(self.geese_positions) < 3:
                    self.game_over = True
                    self.winner = "Fox"
        else:
            if (old_r, old_c) in self.geese_positions:
                self.geese_positions.remove((old_r, old_c))
            self.geese_positions.append((row, col))
            self.check_if_fox_trapped()
        
        self.selected_piece = None
        self.valid_moves = []
        self.fox_turn = not self.fox_turn
        return True
    
    def check_if_fox_trapped(self):
        row, col = self.fox_pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and is_valid_point(nr, nc):
                if self.board[nr][nc] == 0:
                    return False
                if self.board[nr][nc] == 2:
                    jr, jc = nr + dr, nc + dc
                    if 0 <= jr < BOARD_SIZE and 0 <= jc < BOARD_SIZE and is_valid_point(jr, jc) and self.board[jr][jc] == 0:
                        return False
        self.game_over = True
        self.winner = "Geese"
        return True

################################################################################
# Drawing functions
################################################################################
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fox and Geese with Diagonal Move Checks")
clock = pygame.time.Clock()

def draw_board():
    screen.fill(BG_COLOR)
    # Draw orthogonal lines (right and down).
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_point(r, c):
                center_x = c * CELL_SIZE + CELL_SIZE // 2
                center_y = r * CELL_SIZE + CELL_SIZE // 2
                for dr, dc in [(0, 1), (1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and is_valid_point(nr, nc):
                        neigh_x = nc * CELL_SIZE + CELL_SIZE // 2
                        neigh_y = nr * CELL_SIZE + CELL_SIZE // 2
                        pygame.draw.line(screen, LINE_COLOR, (center_x, center_y), (neigh_x, neigh_y), 3)
    
    # Draw diagonal lines in squares where all four corners are valid.
    valid_squares = []
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            if (is_valid_point(r, c) and is_valid_point(r, c+1) and
                is_valid_point(r+1, c) and is_valid_point(r+1, c+1)):
                valid_squares.append((r, c))
    for i, (r, c) in enumerate(valid_squares):
        tl = (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
        tr = ((c+1) * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
        bl = (c * CELL_SIZE + CELL_SIZE // 2, (r+1) * CELL_SIZE + CELL_SIZE // 2)
        br = ((c+1) * CELL_SIZE + CELL_SIZE // 2, (r+1) * CELL_SIZE + CELL_SIZE // 2)
        if (r + c) % 2 == 0:
            pygame.draw.line(screen, LINE_COLOR, tl, br, 3)
        else:
            pygame.draw.line(screen, LINE_COLOR, tr, bl, 3)
    
    # Draw board points.
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_point(r, c):
                center = (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
                pygame.draw.circle(screen, DOT_COLOR, center, 6)

def draw_pieces():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if not is_valid_point(r, c):
                continue
            piece = game_state.board[r][c]
            center = (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
            if piece == 1:  # Fox
                pygame.draw.circle(screen, FOX_COLOR, center, CELL_SIZE // 3)
                pygame.draw.circle(screen, BLACK, center, CELL_SIZE // 3, 2)
                if game_state.selected_piece == (r, c):
                    pygame.draw.circle(screen, HIGHLIGHT_COLOR, center, CELL_SIZE // 3 + 4, 3)
            elif piece == 2:  # Goose
                pygame.draw.circle(screen, GEESE_COLOR, center, CELL_SIZE // 3)
                pygame.draw.circle(screen, BLACK, center, CELL_SIZE // 3, 2)
                if game_state.selected_piece == (r, c):
                    pygame.draw.circle(screen, HIGHLIGHT_COLOR, center, CELL_SIZE // 3 + 4, 3)
    
    # Highlight valid move positions.
    for (mr, mc, _) in game_state.valid_moves:
        center = (mc * CELL_SIZE + CELL_SIZE // 2, mr * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, center, (CELL_SIZE // 3) // 2)

def draw_turn_indicator():
    font = pygame.font.SysFont(None, 30)
    turn_text = "Fox's Turn" if game_state.fox_turn else "Geese's Turn"
    color = FOX_COLOR if game_state.fox_turn else GEESE_COLOR
    text = font.render(turn_text, True, color)
    screen.blit(text, (10, 10))

def draw_game_over():
    if game_state.game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont(None, 72)
        text = font.render(f"{game_state.winner} wins!", True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)
        font_small = pygame.font.SysFont(None, 36)
        restart_text = font_small.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

################################################################################
# Main loop
################################################################################
game_state = GameState()
initialize_diagonal_connections()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_state.game_over:
                game_state = GameState()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_state.game_over:
            mx, my = pygame.mouse.get_pos()
            c = mx // CELL_SIZE
            r = my // CELL_SIZE
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if game_state.selected_piece is None:
                    game_state.select_piece(r, c)
                else:
                    moved = game_state.move_piece(r, c)
                    if not moved:
                        piece_here = game_state.board[r][c]
                        if (game_state.fox_turn and piece_here == 1) or (not game_state.fox_turn and piece_here == 2):
                            game_state.select_piece(r, c)
                        else:
                            game_state.selected_piece = None
                            game_state.valid_moves = []
    draw_board()
    draw_pieces()
    draw_turn_indicator()
    draw_game_over()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
