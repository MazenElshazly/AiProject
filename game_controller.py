from capture import check_winner, apply_captures

from board import Board
from controller import (
    choose_difficulty,
    choose_human_side,
    get_human_move,
    get_computer_move,
    get_legal_moves,
    choose_board_size,
)


# ─────────────────────────────────────────────────────────────
#  WINNER ANNOUNCEMENT
# ─────────────────────────────────────────────────────────────

def _announce_winner(winner, human_side):
    print("\n" + "=" * 52)
    if winner == 'defender':
        print("  DEFENDERS WIN — The King has escaped to a corner!")
    else:
        print("  ATTACKERS WIN — The King has been captured!")

    you_won = (winner == 'attacker' and human_side == 'A') or \
              (winner == 'defender' and human_side == 'D')

    if you_won:
        print("  Congratulations — YOU WIN! 🎉")
    else:
        print("  The computer wins this round. Better luck next time!")
    print("=" * 52)


# ─────────────────────────────────────────────────────────────
#  MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────

def run_game():

    print("=" * 52)
    print("         HNEFATAFL — Viking Chess")
    print("=" * 52)

    # ── Setup ──────────────────────────────────────────────
    board_size = choose_board_size()
    board = Board(board_size)
    board.init_board()

    depth      = choose_difficulty()
    human_side = choose_human_side()
    cpu_side   = "D" if human_side == "A" else "A"

    print(f"\n  You play as   : {'Attacker (A)' if human_side == 'A' else 'Defender (D)'}")
    print(f"  Computer is   : {'Attacker (A)' if cpu_side   == 'A' else 'Defender (D)'}")
    print(f"  Attackers move FIRST.\n")

    current   = "A"   # Attackers always go first
    turn      = 1

    # ── Loop ───────────────────────────────────────────────
    while True:
        print(f"\n{'─' * 52}")
        print(f"  Turn {turn}  |  Playing: {'Attacker (A)' if current == 'A' else 'Defender (D)'}")
        board.print_grid()

        # 1. Check winner BEFORE this player moves
        winner = check_winner(board)
        if winner:
            _announce_winner(winner, human_side)
            break

        # 2. Check for no legal moves (stalemate — current player loses)
        legal = get_legal_moves(board, current)
        if not legal:
            other = "D" if current == "A" else "A"
            print(f"\n  {'Attacker' if current == 'A' else 'Defender'} has no legal moves!")
            _announce_winner('defender' if current == 'A' else 'attacker', human_side)
            break

        # 3. Get the move
        if current == human_side:
            (fr, fc), (tr, tc) = get_human_move(board, current)
        else:
            result = get_computer_move(board, current, depth)
            if result is None:
                # Computer has no moves — other side wins
                other_winner = 'defender' if current == 'A' else 'attacker'
                _announce_winner(other_winner, human_side)
                break
            (fr, fc), (tr, tc) = result

        # 4. Apply the movement using Person 1's board.move()
        piece = board.grid[fr][fc]
        success = board.move(fr, fc, tr, tc, piece_type=piece)

        if not success:
            # board.move() already printed the reason
            print("  Move failed — try again.")
            continue   # don't switch turns, ask again

        # 5. Apply captures (modifies board.grid in-place, returns bool)
        king_captured = apply_captures(board, (tr, tc), current)
        if king_captured:
            board.print_grid()
            _announce_winner('attacker', human_side)
            break

        # 6. Switch sides
        current = "D" if current == "A" else "A"
        turn += 1


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    run_game()