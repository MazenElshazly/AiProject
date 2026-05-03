class Board:
    size = 9
    grid = [[0] * 9 for _ in range(9)]
    center = [4, 4]
    corners = []

    def __init__(self, size=9):
        self.size = size
        self.grid = [["x"] * size for _ in range(size)]
        self.center[0]  = (size //2)
        self.center[1] = (size //2)
        self.corners  = [
            (0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)
        ]

    def print_grid(self):
        # Print column indices at top
        print("   ", end="")
        for col in range(self.size):
            print(f"{col:2} ", end="")
        print()

        # Print top border
        print("  ┌" + "───" * self.size + "┐")

        # Print rows with row indices
        for row in range(self.size):
            print(f"{row:2}│", end="")  # Row index
            for col in range(self.size):
                print(f" {self.grid[row][col]:2}", end="")
            print(" │")

        # Print bottom border
        print("  └" + "───" * self.size + "┘")

        # Print column indices at bottom
        print("   ", end="")
        for col in range(self.size):
            print(f"{col:2} ", end="")
        print()

    def init_board(self):
        cx, cy = self.center

        # el king
        self.grid[cx][cy] = "K"

        # defenders initialisation henaa
        d_coords = [

            (cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1),
            (cx - 1, cy - 1), (cx - 1, cy + 1), (cx + 1, cy - 1), (cx + 1, cy + 1),
            #extra 4 Defenders at edge
            (cx - 2, cy), (cx + 2, cy), (cx, cy - 2), (cx, cy + 2),
        ]

        for r, c in d_coords:
            self.grid[r][c] = "D"

        n = len(self.grid)
        cx, cy = self.center

        dist_to_edge = n // 2 - 1  # e.g. 3 (9x9), 4 (11x11)
        tip_of_attack = n // 2  # e.g. 4 (9x9), 5 (11x11)

        # DOWN
        self.grid[cx + dist_to_edge][cy] = "A"
        for dc in range(-2, 3):
            self.grid[cx + tip_of_attack][cy + dc] = "A"

        # UP
        self.grid[cx - dist_to_edge][cy] = "A"
        for dc in range(-2, 3):
            self.grid[cx - tip_of_attack][cy + dc] = "A"

        # RIGHT
        self.grid[cx][cy + dist_to_edge] = "A"
        for dr in range(-2, 3):
            self.grid[cx + dr][cy + tip_of_attack] = "A"

        # LEFT
        self.grid[cx][cy - dist_to_edge] = "A"
        for dr in range(-2, 3):
            self.grid[cx + dr][cy - tip_of_attack] = "A"


    #Move helpers

    def is_in_bounds(self, row, col):
        return (0 <= row and row < self.size) and (0 <= col and col < self.size)

    def check_straight(self, old_row, old_col, new_row, new_col):
        return (old_row == new_row ) or (old_col == new_col)

    def check_empty_path(self, old_row, old_col, new_row, new_col):
        if old_col == new_col:  # move up or down
            start = min(old_row, new_row)
            end = max(old_row, new_row)
            for row in range(start, end + 1):
                if row == old_row:  # skip starting position
                    continue
                if self.grid[row][new_col] != "x":  # Path is blocked
                    return False
            return True

        else:  # move right or left
            start = min(old_col, new_col)
            end = max(old_col, new_col)
            for col in range(start, end + 1):
                if col == old_col:  # skip starting position
                    continue
                if self.grid[old_row][col] != "x":  # Path is blocked
                    return False
            return True

    def move (self, old_row, old_col, new_row, new_col, piece_type):
        if self.grid[new_row][new_col] == "x" :
            if self.grid[old_row][old_col] == piece_type:
                if self.is_in_bounds(new_row, new_col)  :
                    if self.check_straight(old_row, old_col, new_row, new_col):
                        if self.check_empty_path(old_row, old_col, new_row, new_col):
                            self.grid[new_row][new_col] = piece_type
                            self.grid[old_row][old_col] = "x"
                            return True
                        else:
                            print("opponent in your Path!")
                            return False
                    else:
                        print("cannot move diagonally!")
                        return False
                else:
                    print("out of bounds!")
                    return False
            else:
                print("not your piece to move!")
                return False
        else:
            print("place not Empty!")
            return False


def get_legal_moves(board, player):
    pieces = ["A"] if player == "A" else ["D", "K"]
    moves = []

    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] not in pieces:
                continue

            # Try all four directions, walking until blocked
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                for steps in range(1, board.size):
                    nr, nc = r + dr * steps, c + dc * steps

                    if not board.is_in_bounds(nr, nc):
                        break  # hit the edge

                    if board.grid[nr][nc] != "x":
                        break  # blocked by a piece

                    moves.append(((r, c), (nr, nc)))

    return moves


boardSize = int(input("Enter board size: (9x9 or 11x11)\n"))

while boardSize != 9 and boardSize != 11:
    boardSize = int(input("Enter board size: (9x9 or 11x11)\n"))
board = Board(boardSize)
board.init_board()
board.print_grid()
print(""
      ""
      ""
      "")

board.print_grid()