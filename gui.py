import pygame
import sys
import threading

from board import Board, get_legal_moves
from controller import choose_difficulty, choose_human_side, get_computer_move, choose_board_size
from capture import check_winner, apply_captures

# --- Constants ---
CELL_SIZE = 60
FPS = 30

# --- Colors ---
BG_COLOR = (220, 200, 170)
LINE_COLOR = (50, 50, 50)
THRONE_COLOR = (150, 100, 50)
CORNER_COLOR = (100, 150, 50)

HIGHLIGHT_COLOR = (100, 255, 100, 128) # semi-transparent
SELECTED_COLOR = (255, 255, 100, 128)

ATTACKER_COLOR = (200, 50, 50)
DEFENDER_COLOR = (50, 50, 200)
KING_COLOR = (255, 215, 0)

# --- Drawing ---
def draw_board(screen, board):
    screen.fill(BG_COLOR)
    
    # Draw special squares
    center = board.size // 2
    for r in range(board.size):
        for c in range(board.size):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if r == center and c == center:
                pygame.draw.rect(screen, THRONE_COLOR, rect)
            elif (r, c) in board.corners:
                pygame.draw.rect(screen, CORNER_COLOR, rect)
            
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

def draw_pieces(screen, board):
    for r in range(board.size):
        for c in range(board.size):
            piece = board.grid[r][c]
            if piece != 'x':
                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2
                radius = int(CELL_SIZE * 0.4)
                
                color = None
                if piece == 'A':
                    color = ATTACKER_COLOR
                elif piece == 'D':
                    color = DEFENDER_COLOR
                elif piece == 'K':
                    color = KING_COLOR
                
                if color:
                    pygame.draw.circle(screen, color, (x, y), radius)
                    # draw a border around the piece
                    pygame.draw.circle(screen, LINE_COLOR, (x, y), radius, 2)

def draw_highlights(screen, selected_pos, legal_moves):
    # Need a transparent surface for highlights
    surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    
    if selected_pos:
        sr, sc = selected_pos
        rect = pygame.Rect(sc * CELL_SIZE, sr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, SELECTED_COLOR, rect)
        
        for move in legal_moves:
            (fr, fc), (tr, tc) = move
            if (fr, fc) == selected_pos:
                h_rect = pygame.Rect(tc * CELL_SIZE, tr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, h_rect)
                
    screen.blit(surface, (0, 0))

def run_gui():
    # 1. Ask for options in console first
    print("=" * 52)
    print("         HNEFATAFL — Viking Chess (GUI)")
    print("=" * 52)
    board_size = choose_board_size()
    depth = choose_difficulty()
    human_side = choose_human_side()
    cpu_side = "D" if human_side == "A" else "A"
    
    # 2. Init pygame
    pygame.init()
    width = CELL_SIZE * board_size
    height = CELL_SIZE * board_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Hnefatafl")
    clock = pygame.time.Clock()
    
    # 3. Setup board
    board = Board(board_size)
    board.init_board()
    
    current = "A"
    turn = 1
    
    selected_pos = None
    legal_moves = []
    
    game_over = False
    winner = None
    
    ai_thinking = False
    ai_move_result = False # Use False as 'not ready yet' to differentiate from None (which means no moves)
    
    # --- Helper to handle AI move in a thread so GUI doesn't freeze ---
    def make_ai_move():
        nonlocal ai_move_result
        # get_computer_move returns a move tuple or None
        result = get_computer_move(board, current, depth)
        ai_move_result = result
        
    while True:
        # Check winner before human moves
        if not game_over and check_winner(board):
            winner = check_winner(board)
            game_over = True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if current == human_side and not ai_thinking:
                    # check for no moves
                    all_legal = get_legal_moves(board, current)
                    if not all_legal:
                        winner = 'defender' if current == 'A' else 'attacker'
                        game_over = True
                        continue
                        
                    x, y = event.pos
                    c = x // CELL_SIZE
                    r = y // CELL_SIZE
                    
                    if selected_pos:
                        # Try to move
                        move_attempt = (selected_pos, (r, c))
                        if move_attempt in legal_moves:
                            fr, fc = selected_pos
                            piece = board.grid[fr][fc]
                            success = board.move(fr, fc, r, c, piece)
                            if success:
                                captured = apply_captures(board, (r, c), current)
                                if captured:
                                    winner = 'attacker'
                                    game_over = True
                                
                                current = "D" if current == "A" else "A"
                                turn += 1
                                selected_pos = None
                                legal_moves = []
                                continue
                        else:
                            # If click elsewhere, deselect or select new piece
                            piece = board.grid[r][c]
                            if (current == "A" and piece == "A") or (current == "D" and piece in ["D", "K"]):
                                selected_pos = (r, c)
                                legal_moves = [m for m in all_legal if m[0] == selected_pos]
                            else:
                                selected_pos = None
                                legal_moves = []
                    else:
                        # Select a piece
                        piece = board.grid[r][c]
                        if (current == "A" and piece == "A") or (current == "D" and piece in ["D", "K"]):
                            selected_pos = (r, c)
                            legal_moves = [m for m in all_legal if m[0] == selected_pos]
                            
        # Trigger AI move if it's CPU turn
        if not game_over and current == cpu_side and not ai_thinking:
            ai_thinking = True
            ai_move_result = False
            threading.Thread(target=make_ai_move).start()
            
        # Process AI move if thread finished
        if ai_thinking and ai_move_result is not False:
            if ai_move_result is None:
                winner = 'defender' if current == 'A' else 'attacker'
                game_over = True
            else:
                (fr, fc), (tr, tc) = ai_move_result
                piece = board.grid[fr][fc]
                board.move(fr, fc, tr, tc, piece)
                
                if apply_captures(board, (tr, tc), current):
                    winner = 'attacker'
                    game_over = True
                
                current = "D" if current == "A" else "A"
                turn += 1
                
                win = check_winner(board)
                if win:
                    winner = win
                    game_over = True
            
            ai_thinking = False
            
        # Draw everything
        draw_board(screen, board)
        draw_highlights(screen, selected_pos, legal_moves)
        draw_pieces(screen, board)
        
        if game_over:
            # simple game over text
            font = pygame.font.SysFont(None, 48)
            msg = "DEFENDERS WIN!" if winner == 'defender' else "ATTACKERS WIN!"
            text = font.render(msg, True, (255, 255, 255), (0, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            
            # Draw a slight background for the text so it's readable
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
            
            screen.blit(text, text_rect)
            
        pygame.display.flip()
        clock.tick(48)

if __name__ == '__main__':
    run_gui()
