import pygame
import sys
import threading
import time

from board import Board, get_legal_moves
from controller import choose_difficulty, choose_human_side, get_computer_move, choose_board_size
from capture import check_winner, apply_captures

# --- Constants ---
CELL_SIZE = 60
SIDE_PANEL_WIDTH = 250
FPS = 48
ANIM_DURATION = 0.2  # Seconds for piece movement

# --- Colors ---
BG_COLOR = (220, 200, 170)
PANEL_COLOR = (190, 170, 140)
LINE_COLOR = (50, 50, 50)
THRONE_COLOR = (150, 100, 50)
CORNER_COLOR = (100, 150, 50)

HIGHLIGHT_COLOR = (100, 255, 100, 128) # semi-transparent
SELECTED_COLOR = (255, 255, 100, 128)

ATTACKER_COLOR = (200, 50, 50)
DEFENDER_COLOR = (50, 50, 200)
KING_COLOR = (255, 215, 0)
TEXT_COLOR = (30, 30, 30)

# --- Drawing ---
def draw_board(screen, board):
    # Fill the board area only
    board_rect = pygame.Rect(0, 0, board.size * CELL_SIZE, board.size * CELL_SIZE)
    pygame.draw.rect(screen, BG_COLOR, board_rect)
    
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

def draw_piece_at(screen, piece, x, y):
    radius = int(CELL_SIZE * 0.4)
    color = None
    if piece == 'A':
        color = ATTACKER_COLOR
    elif piece == 'D':
        color = DEFENDER_COLOR
    elif piece == 'K':
        color = KING_COLOR
    
    if color:
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        # draw a border around the piece
        pygame.draw.circle(screen, LINE_COLOR, (int(x), int(y)), radius, 2)

def draw_pieces(screen, board, skip_pos=None):
    for r in range(board.size):
        for c in range(board.size):
            if skip_pos and (r, c) == skip_pos:
                continue
            piece = board.grid[r][c]
            if piece != 'x':
                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2
                draw_piece_at(screen, piece, x, y)

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

def draw_side_panel(screen, board_width, height, cap_att, cap_def, game_over, restart_rect):
    panel_rect = pygame.Rect(board_width, 0, SIDE_PANEL_WIDTH, height)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect)
    pygame.draw.line(screen, LINE_COLOR, (board_width, 0), (board_width, height), 3)
    
    font = pygame.font.SysFont(None, 32)
    title_font = pygame.font.SysFont(None, 40)
    
    title = title_font.render("Captures", True, TEXT_COLOR)
    screen.blit(title, (board_width + 20, 20))
    
    # Draw Attacker stats
    pygame.draw.circle(screen, ATTACKER_COLOR, (board_width + 40, 90), 15)
    pygame.draw.circle(screen, LINE_COLOR, (board_width + 40, 90), 15, 2)
    att_text = font.render(f"Lost: {cap_att}", True, TEXT_COLOR)
    screen.blit(att_text, (board_width + 70, 80))
    
    # Draw Defender stats
    pygame.draw.circle(screen, DEFENDER_COLOR, (board_width + 40, 140), 15)
    pygame.draw.circle(screen, LINE_COLOR, (board_width + 40, 140), 15, 2)
    def_text = font.render(f"Lost: {cap_def}", True, TEXT_COLOR)
    screen.blit(def_text, (board_width + 70, 130))

    if game_over:
        pygame.draw.rect(screen, (200, 200, 200), restart_rect)
        pygame.draw.rect(screen, LINE_COLOR, restart_rect, 2)
        btn_text = font.render("RESTART", True, TEXT_COLOR)
        btn_rect = btn_text.get_rect(center=restart_rect.center)
        screen.blit(btn_text, btn_rect)

def run_gui():
    print("=" * 52)
    print("         HNEFATAFL — Viking Chess (GUI)")
    print("=" * 52)
    board_size = choose_board_size()
    depth = choose_difficulty()
    human_side = choose_human_side()
    cpu_side = "D" if human_side == "A" else "A"
    
    pygame.init()
    board_width = CELL_SIZE * board_size
    height = CELL_SIZE * board_size
    width = board_width + SIDE_PANEL_WIDTH
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Hnefatafl")
    clock = pygame.time.Clock()
    
    board = Board(board_size)
    board.init_board()
    
    current = "A"
    turn = 1
    
    selected_pos = None
    legal_moves = []
    
    game_over = False
    winner = None
    
    ai_thinking = False
    ai_move_result = False
    
    captured_attackers = 0
    captured_defenders = 0
    
    pending_move = None
    capture_effects = []
    
    restart_rect = pygame.Rect(board_width + 25, height - 80, SIDE_PANEL_WIDTH - 50, 50)
    
    def make_ai_move():
        nonlocal ai_move_result
        result = get_computer_move(board, current, depth)
        ai_move_result = result
        
    while True:
        current_time = time.time()
        capture_effects = [e for e in capture_effects if current_time - e['start'] < 0.6]

        if not game_over and not pending_move and check_winner(board):
            winner = check_winner(board)
            game_over = True
            
        if pending_move:
            progress = (current_time - pending_move['start_time']) / ANIM_DURATION
            if progress >= 1.0:
                fr, fc = pending_move['from']
                tr, tc = pending_move['to']
                piece = pending_move['piece']
                
                # Apply logical move
                board.move(fr, fc, tr, tc, piece)
                king_captured, victims = apply_captures(board, (tr, tc), current)
                
                # Track captures and effects
                for vr, vc in victims:
                    capture_effects.append({'pos': (vr, vc), 'start': current_time})
                    if current == "A":
                        captured_defenders += 1
                    else:
                        captured_attackers += 1
                        
                if king_captured:
                    winner = 'attacker'
                    game_over = True
                    
                current = "D" if current == "A" else "A"
                turn += 1
                
                win = check_winner(board)
                if win:
                    winner = win
                    game_over = True
                    
                pending_move = None
                selected_pos = None
                legal_moves = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    if restart_rect.collidepoint(event.pos):
                        # Restart logic
                        board = Board(board_size)
                        board.init_board()
                        current = "A"
                        turn = 1
                        game_over = False
                        winner = None
                        captured_attackers = 0
                        captured_defenders = 0
                        pending_move = None
                        capture_effects = []
                        ai_thinking = False
                        ai_move_result = False
                        selected_pos = None
                        legal_moves = []
                    continue

                if not pending_move and current == human_side and not ai_thinking:
                    all_legal = get_legal_moves(board, current)
                    if not all_legal:
                        winner = 'defender' if current == 'A' else 'attacker'
                        game_over = True
                        continue
                        
                    x, y = event.pos
                    if x < board_width:
                        c = x // CELL_SIZE
                        r = y // CELL_SIZE
                        
                        if selected_pos:
                            move_attempt = (selected_pos, (r, c))
                            if move_attempt in legal_moves:
                                fr, fc = selected_pos
                                piece = board.grid[fr][fc]
                                # Instead of board.move, set pending_move to trigger animation
                                pending_move = {
                                    'from': selected_pos,
                                    'to': (r, c),
                                    'piece': piece,
                                    'start_time': current_time
                                }
                            else:
                                piece = board.grid[r][c]
                                if (current == "A" and piece == "A") or (current == "D" and piece in ["D", "K"]):
                                    selected_pos = (r, c)
                                    legal_moves = [m for m in all_legal if m[0] == selected_pos]
                                else:
                                    selected_pos = None
                                    legal_moves = []
                        else:
                            piece = board.grid[r][c]
                            if (current == "A" and piece == "A") or (current == "D" and piece in ["D", "K"]):
                                selected_pos = (r, c)
                                legal_moves = [m for m in all_legal if m[0] == selected_pos]
                            
        if not game_over and current == cpu_side and not ai_thinking and not pending_move:
            ai_thinking = True
            ai_move_result = False
            threading.Thread(target=make_ai_move).start()
            
        if ai_thinking and ai_move_result is not False and not pending_move:
            if ai_move_result is None:
                winner = 'defender' if current == 'A' else 'attacker'
                game_over = True
            else:
                (fr, fc), (tr, tc) = ai_move_result
                piece = board.grid[fr][fc]
                pending_move = {
                    'from': (fr, fc),
                    'to': (tr, tc),
                    'piece': piece,
                    'start_time': current_time
                }
            ai_thinking = False
            
        # Draw everything
        screen.fill(BG_COLOR) # clear everything
        draw_board(screen, board)
        draw_side_panel(screen, board_width, height, captured_attackers, captured_defenders, game_over, restart_rect)
        draw_highlights(screen, selected_pos, legal_moves)
        
        skip_pos = pending_move['from'] if pending_move else None
        draw_pieces(screen, board, skip_pos)
        
        # Draw animating piece
        if pending_move:
            progress = (current_time - pending_move['start_time']) / ANIM_DURATION
            progress = max(0.0, min(1.0, progress))
            fr, fc = pending_move['from']
            tr, tc = pending_move['to']
            piece = pending_move['piece']
            
            sx = fc * CELL_SIZE + CELL_SIZE // 2
            sy = fr * CELL_SIZE + CELL_SIZE // 2
            ex = tc * CELL_SIZE + CELL_SIZE // 2
            ey = tr * CELL_SIZE + CELL_SIZE // 2
            
            cx = sx + (ex - sx) * progress
            cy = sy + (ey - sy) * progress
            
            draw_piece_at(screen, piece, cx, cy)
            
        # Draw capture effects (floating 'X')
        for effect in capture_effects:
            r, c = effect['pos']
            elapsed = current_time - effect['start']
            alpha = max(0, int(255 * (1 - elapsed / 0.6)))
            font = pygame.font.SysFont(None, 50)
            text = font.render("X", True, (255, 0, 0))
            text.set_alpha(alpha)
            
            # float upwards
            y_offset = int(elapsed * 40)
            x = c * CELL_SIZE + CELL_SIZE // 2
            y = r * CELL_SIZE + CELL_SIZE // 2 - y_offset
            
            rect = text.get_rect(center=(x, y))
            screen.blit(text, rect)
        
        if game_over:
            font = pygame.font.SysFont(None, 48)
            msg = "DEFENDERS WIN!" if winner == 'defender' else "ATTACKERS WIN!"
            text = font.render(msg, True, (255, 255, 255))
            text_rect = text.get_rect(center=(board_width//2, height//2))
            
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
            
            screen.blit(text, text_rect)
            
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    run_gui()
