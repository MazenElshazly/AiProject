size = 9
grid = [[0] * size for _ in range(size)]

# Now you can access any cell
grid[0][0] = 42
grid[8][8] = 100

print(grid[8][8])  # 100