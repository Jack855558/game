import pygame
import sys
import random

pygame.init()

# Window and board settings: 800x800 size
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 7  # 7x7 grid underlying the plus-shaped board
CELL_SIZE = WIDTH // BOARD_SIZE
BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE
BOARD_OFFSET_X = (WIDTH - BOARD_PIXEL_SIZE) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_PIXEL_SIZE) // 2

# Colors
BG_COLOR = (210, 180, 140)      # Tan background
LINE_COLOR = (101, 67, 33)      # Brown for connecting lines
DOT_COLOR = (0, 0, 0)           # Black for board points
FOX_COLOR = (255, 69, 0)        # Red-orange for fox
GEESE_COLOR = (220, 220, 220)   # Light gray for geese
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow for highlights
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

##########################################################################
# Board definition: A cell is valid if its row or column is in [2, 3, 4].
##########################################################################
def is_valid_point(row, col):
    return (row in [2, 3, 4]) or (col in [2, 3, 4])

# Dictionary to store valid diagonal connections.
diagonal_connections = {}

def initialize_diagonal_connections():
    """Create a mapping of all valid diagonal connections on the board."""
    global diagonal_connections
    diagonal_connections.clear()
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            if (is_valid_point(r, c) and is_valid_point(r, c+1) and
                is_valid_point(r+1, c) and is_valid_point(r+1, c+1)):
                tl = (r, c)       # top-left
                tr = (r, c+1)     # top-right
                bl = (r+1, c)     # bottom-left
                br = (r+1, c+1)   # bottom-right
                if (r + c) % 2 == 0:  # Diagonal from top-left to bottom-right
                    diagonal_connections[(tl, br)] = True
                    diagonal_connections[(br, tl)] = True
                else:  # Diagonal from top-right to bottom-left
                    diagonal_connections[(tr, bl)] = True
                    diagonal_connections[(bl, tr)] = True

def has_diagonal_connection(row, col, dr, dc):
    """Check for an actual diagonal connection from (row, col) in direction (dr, dc)."""
    target_row, target_col = row + dr, col + dc
    return ((row, col), (target_row, target_col)) in diagonal_connections

################################################################################
# Game state
################################################################################
class GameState:
    def __init__(self):
        # Create board: valid cells get 0; invalid cells are None.
        self.board = []
        for row in range(BOARD_SIZE):
            row_list = []
            for col in range(BOARD_SIZE):
                row_list.append(0 if is_valid_point(row, col) else None)
            self.board.append(row_list)
        
        # Place fox at center (3,3)
        self.fox_pos = (3, 3)
        self.board[3][3] = 1

        # Place geese:
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
        # Geese turn: select a goose.
        if not self.fox_turn and self.board[row][col] == 2:
            self.selected_piece = (row, col)
            self.calculate_valid_moves()
            return True
        # Fox turn: select the fox.
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
        
        if piece_type == 1:  # Fox moves: all 8 directions.
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_r, new_c = row + dr, col + dc
                if dr != 0 and dc != 0:
                    if not has_diagonal_connection(row, col, dr, dc):
                        continue
                if 0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE and is_valid_point(new_r, new_c):
                    if self.board[new_r][new_c] == 0:
                        self.valid_moves.append((new_r, new_c, None))
                    elif self.board[new_r][new_c] == 2:
                        jump_r, jump_c = new_r + dr, new_c + dc
                        if (0 <= jump_r < BOARD_SIZE and 0 <= jump_c < BOARD_SIZE and 
                            is_valid_point(jump_r, jump_c) and self.board[jump_r][jump_c] == 0):
                            if dr != 0 and dc != 0:
                                if not (has_diagonal_connection(row, col, dr, dc) and 
                                        has_diagonal_connection(new_r, new_c, dr, dc)):
                                    continue
                            self.valid_moves.append((jump_r, jump_c, (new_r, new_c)))
        elif piece_type == 2:  # Geese moves: forward and diagonally upward.
            directions = [(-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
            for dr, dc in directions:
                new_r, new_c = row + dr, col + dc
                if dr != 0 and dc != 0:
                    if not has_diagonal_connection(row, col, dr, dc):
                        continue
                if 0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE:
                    if is_valid_point(new_r, new_c) and self.board[new_r][new_c] == 0:
                        self.valid_moves.append((new_r, new_c, None))
    
    def move_piece(self, row, col):
        if (not self.selected_piece or 
            (row, col) not in [(m[0], m[1]) for m in self.valid_moves]):
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
        # Switch turn.
        self.fox_turn = not self.fox_turn
        # Check if the new active player has any legal moves.
        self.check_for_game_over_on_turn()
        return True

    def check_if_fox_trapped(self):
        # Existing check after a goose move.
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
                    if (0 <= jr < BOARD_SIZE and 0 <= jc < BOARD_SIZE and 
                        is_valid_point(jr, jc) and self.board[jr][jc] == 0):
                        return False
        self.game_over = True
        self.winner = "Geese"
        return True

    def check_for_game_over_on_turn(self):
        """Check if the current player (fox or geese) has any valid moves.
           If not, end the game accordingly."""
        if self.fox_turn:
            fox_r, fox_c = self.fox_pos
            moves = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_r, new_c = fox_r + dr, fox_c + dc
                if dr != 0 and dc != 0:
                    if not has_diagonal_connection(fox_r, fox_c, dr, dc):
                        continue
                if (0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE and 
                    is_valid_point(new_r, new_c)):
                    if self.board[new_r][new_c] == 0:
                        moves.append((new_r, new_c))
                    elif self.board[new_r][new_c] == 2:
                        jump_r, jump_c = new_r + dr, new_c + dc
                        if (0 <= jump_r < BOARD_SIZE and 0 <= jump_c < BOARD_SIZE and 
                            is_valid_point(jump_r, jump_c) and self.board[jump_r][jump_c] == 0):
                            if dr != 0 and dc != 0:
                                if not (has_diagonal_connection(fox_r, fox_c, dr, dc) and 
                                        has_diagonal_connection(new_r, new_c, dr, dc)):
                                    continue
                            moves.append((jump_r, jump_c))
            if not moves:
                self.game_over = True
                self.winner = "Geese"
        else:
            # Check if at least one goose can move.
            possible = False
            for (r, c) in self.geese_positions:
                directions = [(-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if dr != 0 and dc != 0:
                        if not has_diagonal_connection(r, c, dr, dc):
                            continue
                    if (0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE and 
                        is_valid_point(new_r, new_c) and self.board[new_r][new_c] == 0):
                        possible = True
                        break
                if possible:
                    break
            if not possible:
                self.game_over = True
                self.winner = "Fox"

################################################################################
# Confetti effect classes and functions
################################################################################
# For web projects you might install canvas-confetti via:
#   npm install canvas-confetti
# Here we simulate confetti using a simple particle system.
class ConfettiParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.uniform(-50, 0)
        self.speed = random.uniform(100, 300)
        self.dx = random.uniform(-50, 50)
        self.color = random.choice([
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ])
        self.size = random.randint(3, 7)
    
    def update(self, dt):
        self.y += self.speed * dt
        self.x += self.dx * dt
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y > HEIGHT:
            self.y = random.uniform(-50, 0)
            self.x = random.randint(0, WIDTH)

confetti_particles = []  # Global list for confetti particles

def update_confetti(dt):
    for particle in confetti_particles:
        particle.update(dt)

def draw_confetti():
    for particle in confetti_particles:
        pygame.draw.circle(screen, particle.color, (int(particle.x), int(particle.y)), particle.size)

################################################################################
# Drawing functions: board, pieces, turn indicator, game over
################################################################################
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fox and Geese with Settings & Confetti")
clock = pygame.time.Clock()

def draw_board():
    screen.fill(BG_COLOR)
    # Draw orthogonal lines with board offset.
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_point(r, c):
                center_x = BOARD_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                center_y = BOARD_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                for dr, dc in [(0, 1), (1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and 
                        is_valid_point(nr, nc)):
                        neigh_x = BOARD_OFFSET_X + nc * CELL_SIZE + CELL_SIZE // 2
                        neigh_y = BOARD_OFFSET_Y + nr * CELL_SIZE + CELL_SIZE // 2
                        pygame.draw.line(screen, LINE_COLOR, (center_x, center_y), (neigh_x, neigh_y), 3)
    
    # Draw diagonal lines in valid squares.
    valid_squares = []
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            if (is_valid_point(r, c) and is_valid_point(r, c+1) and
                is_valid_point(r+1, c) and is_valid_point(r+1, c+1)):
                valid_squares.append((r, c))
    for r, c in valid_squares:
        tl = (BOARD_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2, 
              BOARD_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2)
        tr = (BOARD_OFFSET_X + (c+1) * CELL_SIZE + CELL_SIZE // 2, 
              BOARD_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2)
        bl = (BOARD_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2, 
              BOARD_OFFSET_Y + (r+1) * CELL_SIZE + CELL_SIZE // 2)
        br = (BOARD_OFFSET_X + (c+1) * CELL_SIZE + CELL_SIZE // 2, 
              BOARD_OFFSET_Y + (r+1) * CELL_SIZE + CELL_SIZE // 2)
        if (r + c) % 2 == 0:
            pygame.draw.line(screen, LINE_COLOR, tl, br, 3)
        else:
            pygame.draw.line(screen, LINE_COLOR, tr, bl, 3)
    
    # Draw board points.
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if is_valid_point(r, c):
                center = (BOARD_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2,
                          BOARD_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2)
                pygame.draw.circle(screen, DOT_COLOR, center, 6)

def draw_pieces():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if not is_valid_point(r, c):
                continue
            piece = game_state.board[r][c]
            center = (BOARD_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2,
                      BOARD_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2)
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
    
    for (mr, mc, _) in game_state.valid_moves:
        center = (BOARD_OFFSET_X + mc * CELL_SIZE + CELL_SIZE // 2,
                  BOARD_OFFSET_Y + mr * CELL_SIZE + CELL_SIZE // 2)
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
# UI Elements: Settings button, animated dropdown, and rules modal
################################################################################
SETTINGS_BUTTON_RECT = pygame.Rect(WIDTH - 50, 10, 40, 40)
DROPDOWN_WIDTH = 150
DROPDOWN_X = WIDTH - 10 - DROPDOWN_WIDTH  # right-aligned with a 10px margin
DROPDOWN_Y = SETTINGS_BUTTON_RECT.bottom  # just below the settings button
DROPDOWN_BUTTON_HEIGHT = 40
DROPDOWN_BUTTON_SPACING = 10
DROPDOWN_TARGET_HEIGHT = 4 * DROPDOWN_BUTTON_HEIGHT + 3 * DROPDOWN_BUTTON_SPACING

dropdown_anim_height = 0
dropdown_open = False

# Update dropdown_buttons: set "2P" action to reset the game.
dropdown_buttons = [
    {"label": "2P", "action": "reset"},
    {"label": "AI Fox", "action": None},
    {"label": "AI Geese", "action": None},
    {"label": "Rules", "action": "open_rules"}
]

rules_open = False

def draw_settings_button():
    # Define the adjusted button properties
    new_width = 90  # Make the button longer
    new_x = SETTINGS_BUTTON_RECT.x - 22  # Move it left

    # Create a new rectangle for drawing without affecting the original
    adjusted_rect = pygame.Rect(new_x, SETTINGS_BUTTON_RECT.y, new_width, SETTINGS_BUTTON_RECT.height)

    # Draw a drop shadow for depth
    shadow_offset = 3
    shadow_rect = adjusted_rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=8)

    # Draw the main button
    pygame.draw.rect(screen, (150, 150, 150), adjusted_rect, border_radius=8)

    # Render the text centered in the button
    font = pygame.font.SysFont(None, 24)
    text = font.render("SETTINGS", True, BLACK)
    text_rect = text.get_rect(center=adjusted_rect.center)
    screen.blit(text, text_rect)

    return adjusted_rect  # Return the new rect for click detection

# Store the updated rect for click handling
SETTINGS_BUTTON_RECT = draw_settings_button()



def update_dropdown(dt):
    global dropdown_anim_height
    speed = 500  # pixels per second for the animation
    if dropdown_open:
        dropdown_anim_height += speed * dt
        if dropdown_anim_height > DROPDOWN_TARGET_HEIGHT:
            dropdown_anim_height = DROPDOWN_TARGET_HEIGHT
    else:
        dropdown_anim_height -= speed * dt
        if dropdown_anim_height < 0:
            dropdown_anim_height = 0

def draw_dropdown_menu():
    if dropdown_anim_height <= 0:
        return
    dropdown_rect = pygame.Rect(DROPDOWN_X, DROPDOWN_Y, DROPDOWN_WIDTH, dropdown_anim_height)
    # Draw a drop shadow for the dropdown container.
    shadow_rect = dropdown_rect.copy()
    shadow_rect.topleft = (dropdown_rect.left + 3, dropdown_rect.top + 3)
    pygame.draw.rect(screen, (150, 150, 150), shadow_rect, border_radius=8)
    pygame.draw.rect(screen, (240, 240, 240), dropdown_rect, border_radius=8)
    old_clip = screen.get_clip()
    screen.set_clip(dropdown_rect)
    font = pygame.font.SysFont(None, 24)
    for i, button in enumerate(dropdown_buttons):
        btn_y = DROPDOWN_Y + i * (DROPDOWN_BUTTON_HEIGHT + DROPDOWN_BUTTON_SPACING)
        btn_rect = pygame.Rect(DROPDOWN_X, btn_y, DROPDOWN_WIDTH, DROPDOWN_BUTTON_HEIGHT)
        # Draw a shadow for each button.
        shadow_btn = btn_rect.move(2, 2)
        pygame.draw.rect(screen, (100, 100, 100), shadow_btn, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, btn_rect, 2, border_radius=8)
        label_text = font.render(button["label"], True, BLACK)
        label_rect = label_text.get_rect(center=btn_rect.center)
        screen.blit(label_text, label_rect)
    screen.set_clip(old_clip)

def draw_rules_modal():
    if not rules_open:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    modal_width, modal_height = int(WIDTH * 0.7), int(HEIGHT * 0.7)
    modal_x = (WIDTH - modal_width) // 2
    modal_y = (HEIGHT - modal_height) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
    pygame.draw.rect(screen, WHITE, modal_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, modal_rect, 3, border_radius=8)
    
    close_button_size = 30
    close_button_rect = pygame.Rect(modal_x + modal_width - close_button_size - 10, modal_y + 10, close_button_size, close_button_size)
    pygame.draw.rect(screen, (200, 0, 0), close_button_rect, border_radius=8)
    close_font = pygame.font.SysFont(None, 24)
    close_text = close_font.render("X", True, WHITE)
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    rules_text = (
        "Fox and Geese Rules:\n\n"
        "- The game is played on a plus-shaped board.\n"
        "- One player controls the fox (moves in all 8 directions).\n"
        "- The other controls the geese (move forward and diagonally upward).\n"
        "- The fox can capture geese by jumping over them.\n"
        "- Geese win by trapping the fox so it cannot move.\n"
        "- Fox wins by capturing enough geese (fewer than 3 remain).\n\n"
    )
    lines = rules_text.split("\n")
    rules_font = pygame.font.SysFont(None, 24)
    line_height = rules_font.get_linesize()
    text_x = modal_x + 20
    text_y = modal_y + 60
    for line in lines:
        text_surface = rules_font.render(line, True, BLACK)
        screen.blit(text_surface, (text_x, text_y))
        text_y += line_height + 5
    
    return close_button_rect

def handle_dropdown_click(pos):
    global rules_open, game_state, confetti_particles, dropdown_open
    if pos[0] < DROPDOWN_X or pos[0] > DROPDOWN_X + DROPDOWN_WIDTH:
        return False
    if pos[1] < DROPDOWN_Y or pos[1] > DROPDOWN_Y + dropdown_anim_height:
        return False
    for i, button in enumerate(dropdown_buttons):
        btn_y = DROPDOWN_Y + i * (DROPDOWN_BUTTON_HEIGHT + DROPDOWN_BUTTON_SPACING)
        btn_rect = pygame.Rect(DROPDOWN_X, btn_y, DROPDOWN_WIDTH, DROPDOWN_BUTTON_HEIGHT)
        if btn_rect.collidepoint(pos):
            # If the button action is "reset", reset the game.
            if button["action"] == "reset":
                game_state = GameState()
                confetti_particles.clear()
            elif button["action"] == "open_rules":
                rules_open = True
            # Close the dropdown after an action.
            dropdown_open = False
            return True
    return False

################################################################################
# Main loop
################################################################################
game_state = GameState()
initialize_diagonal_connections()
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta time (seconds)
    update_dropdown(dt)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_state.game_over:
                game_state = GameState()
                confetti_particles.clear()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if rules_open:
                modal_width, modal_height = int(WIDTH * 0.7), int(HEIGHT * 0.7)
                modal_x = (WIDTH - modal_width) // 2
                modal_y = (HEIGHT - modal_height) // 2
                close_button_size = 30
                close_button_rect = pygame.Rect(modal_x + modal_width - close_button_size - 10, modal_y + 10, close_button_size, close_button_size)
                if close_button_rect.collidepoint((mx, my)):
                    rules_open = False
                continue
            
            if SETTINGS_BUTTON_RECT.collidepoint((mx, my)):
                dropdown_open = not dropdown_open
                continue
            
            if dropdown_anim_height > 0:
                if handle_dropdown_click((mx, my)):
                    continue
            
            if (BOARD_OFFSET_X <= mx <= BOARD_OFFSET_X + BOARD_PIXEL_SIZE and 
                BOARD_OFFSET_Y <= my <= BOARD_OFFSET_Y + BOARD_PIXEL_SIZE):
                board_x = mx - BOARD_OFFSET_X
                board_y = my - BOARD_OFFSET_Y
                c = board_x // CELL_SIZE
                r = board_y // CELL_SIZE
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if game_state.selected_piece is None:
                        game_state.select_piece(r, c)
                    else:
                        moved = game_state.move_piece(r, c)
                        if not moved:
                            piece_here = game_state.board[r][c]
                            if ((game_state.fox_turn and piece_here == 1) or 
                                (not game_state.fox_turn and piece_here == 2)):
                                game_state.select_piece(r, c)
                            else:
                                game_state.selected_piece = None
                                game_state.valid_moves = []
    
    draw_board()
    draw_pieces()
    draw_turn_indicator()
    draw_settings_button()
    draw_dropdown_menu()
    if rules_open:
        draw_rules_modal()
    
    if game_state.game_over:
        draw_game_over()
        if not confetti_particles:
            confetti_particles = [ConfettiParticle() for _ in range(100)]
        update_confetti(dt)
        draw_confetti()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
