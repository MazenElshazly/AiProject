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
        for row in range(self.size):
            for col in range(self.size):
                 print(self.grid[row][col],end = "  ")
            print()

    def initBoard(self):
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





board = Board(9)
board.initBoard()
board.print_grid()