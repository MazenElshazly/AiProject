from board import Board
def _is_anvil(board, far_r, far_c, capturing_side):
    if not board.is_in_bounds(far_r, far_c):  # add this
        return False
    if (far_r, far_c) == tuple(board.center) or (far_r, far_c) in board.corners:
        return True
    if capturing_side == "A" and board.grid[far_r][far_c] == "A":
        return True
    if capturing_side == "D" and board.grid[far_r][far_c] == "D":
        return True
    return False



def _custodial_captures(board, moved_to, capturing_side):
    tr, tc = moved_to
    to_remove = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = tr + dr, tc + dc
        if not board.is_in_bounds(nr, nc):
            continue
        victim = board.grid[nr][nc]
        if capturing_side == "A" and victim != "D":
            continue
        if capturing_side == "D" and victim != "A":
            continue
        far_r, far_c = nr + dr, nc + dc
        if _is_anvil(board, far_r, far_c, capturing_side):
            to_remove.append((nr, nc))
    return to_remove



def king_captured(board):
    king_pos = None
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] == "K":
                king_pos = (r, c)
                break
        if king_pos:
            break
    if king_pos is None:
        return True
    kr, kc = king_pos
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = kr + dr, kc + dc
        if not board.is_in_bounds(nr, nc):
            continue
        if board.grid[nr][nc] != "A":
            return False
    return True



def check_winner(board):
    king_pos = None
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] == "K":
                king_pos = (r, c)
                break
        if king_pos:
            break
    if king_captured(board):
        return 'attacker'
    if king_pos is None:
        return 'attacker'
    if king_pos in board.corners:
        return 'defender'
    return None


def apply_captures(board, moved_to, capturing_side):
    victims = _custodial_captures(board, moved_to, capturing_side)
    for vr, vc in victims:
        board.grid[vr][vc] = "x"

    if capturing_side == "A" and king_captured(board):
        return True
    return False