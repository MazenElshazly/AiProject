from ai import get_best_move
from board import get_legal_moves

DIFFICULTY_DEPTH = {
    'easy': 1,
    'medium': 3,
    'hard': 5
}

def choose_difficulty():

    """
    Ask the player to pick Easy / Medium / Hard at game start.
    Returns the integer depth the AI should search to.
    """
    print("\n  Select difficulty:")
    print("    1. Easy   (AI looks 1 move ahead)")
    print("    2. Medium (AI looks 3 moves ahead)")
    print("    3. Hard   (AI looks 5 moves ahead)")
    while True:
        c = input("  >> ").strip()
        if c == '1': return DIFFICULTY_DEPTH['easy']
        if c == '2': return DIFFICULTY_DEPTH['medium']
        if c == '3': return DIFFICULTY_DEPTH['hard']
        print("  Enter 1, 2, or 3.")


def choose_human_side():
    """
    Ask the player which side they want.
    Returns "A" (attacker) or "D" (defender).

    Note: Attackers always move FIRST per official rules.
    """
    print("\n  Choose your side:")
    print("    1. Attacker (A) — 24 pieces, moves FIRST, captures the King")
    print("    2. Defender (D) — 12 pieces + King, escort King to a corner")
    while True:
        c = input("  >> ").strip()
        if c == '1': return "A"
        if c == '2': return "D"
        print("  Enter 1 or 2.")


def choose_board_size():
    """
    Ask the player to choose the board size.
    Returns 9 or 11.
    """
    print("\n  Choose board size:")
    print("    1. 9x9")
    print("    2. 11x11")
    while True:
        c = input("  >> ").strip()
        if c == '1': return 9
        if c == '2': return 11
        print("  Enter 1 or 2.")

# ─────────────────────────────────────────────────────────────
#  MOVE GENERATION  (legal moves for a given side)
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
#  HUMAN INPUT
# ─────────────────────────────────────────────────────────────

def _parse_input(raw):
    """
    Parse raw text into a move tuple.

    Accepted formats:
      "2 4 2 7"    space-separated  → from_row from_col to_row to_col
      "2,4 2,7"    comma-separated  (same thing)

    Returns ((fr, fc), (tr, tc)) or None on bad input.
    """
    raw = raw.strip().replace(',', ' ')
    parts = raw.split()
    if len(parts) != 4:
        return None
    try:
        fr, fc, tr, tc = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        return (fr, fc), (tr, tc)
    except ValueError:
        return None


def get_human_move(board, player):
    """
    Prompt the human for a move, run all validation checks, and
    return only when a fully legal move has been entered.

    Validation order:
      1. Format   — must be 4 integers
      2. Bounds   — all coordinates on the board
      3. Ownership— the piece at (from_row, from_col) must belong to player
      4. Legality — must appear in get_legal_moves()

    Type 'quit' to exit the game at any time.

    Returns ((from_row, from_col), (to_row, to_col))
    """
    legal = get_legal_moves(board, player)
    legal_set = set(legal)
    label = "Attacker" if player == "A" else "Defender"

    print(f"\n  [{label}] Your turn.")
    print("  Enter:  from_row  from_col  to_row  to_col")
    print("  Example: 4 2 4 6   — moves piece at row 4, col 2  →  row 4, col 6")
    print("  Type 'quit' to exit.\n")

    while True:
        raw = input("  >> ").strip()

        if raw.lower() in ('q', 'quit', 'exit'):
            print("\n  Thanks for playing. Goodbye!")
            raise SystemExit

        # 1. Format
        move = _parse_input(raw)
        if move is None:
            print("  Bad format — enter four numbers e.g. 4 2 4 6")
            continue

        (fr, fc), (tr, tc) = move

        # 2. Bounds
        if not (board.is_in_bounds(fr, fc) and board.is_in_bounds(tr, tc)):
            print(f"  Out of range — coordinates must be 0 to {board.size - 1}.")
            continue

        # 3. Ownership
        piece = board.grid[fr][fc]
        if player == "A" and piece != "A":
            print(f"  No attacker at ({fr},{fc}). Pick one of your 'A' pieces.")
            continue
        if player == "D" and piece not in ("D", "K"):
            print(f"  No defender/king at ({fr},{fc}). Pick one of your 'D' or 'K' pieces.")
            continue

        # 4. Legality
        if move not in legal_set:
            print("  Illegal move — path blocked or destination occupied.")
            continue

        return move


# ─────────────────────────────────────────────────────────────
#  COMPUTER MOVE
# ─────────────────────────────────────────────────────────────

def get_computer_move(board, player, depth):

    label = "Attacker" if player == "A" else "Defender"
    print(f"\n  [Computer — {label}] Thinking... (depth {depth})")
# yasso eb2a garab de lama t implement best move
    move = get_best_move(board, player, depth)
    if move is None:
        print("  Computer has no legal moves.")
        return None
    (fr, fc), (tr, tc) = move
    print(f"  Computer plays: ({fr},{fc}) → ({tr},{tc})")
    return move