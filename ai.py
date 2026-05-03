from capture import check_winner, apply_captures
from board import Board, get_legal_moves

WIN_SCORE = 10000
KING_DISTANCE_WEIGHT = 50
MATERIAL_WEIGHT = 10


def clone_board(currentBoard: Board):
    newBoard = Board(size=currentBoard.size)
    newBoard.grid = [row[:] for row in currentBoard.grid] 
    newBoard.center = list(currentBoard.center)           
    return newBoard

def evaluate(board, aiPlayer):
    winner = check_winner(board)
    if winner == 'attacker':
        if aiPlayer == 'A':
            return WIN_SCORE
        else:
            return -WIN_SCORE
    if winner == 'defender':
        if aiPlayer == 'D':
            return WIN_SCORE
        else:
            return -WIN_SCORE

    score = 0
    attackerCount = sum(row.count("A") for row in board.grid)
    defenderCount = sum(row.count("D") for row in board.grid)   
    
    if aiPlayer == 'A':
        score += MATERIAL_WEIGHT * (attackerCount - defenderCount)
    else:
        score += MATERIAL_WEIGHT * (defenderCount - attackerCount)

    kingPosition = None
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] == 'K':
                kingPosition = (r, c)
                break
        if kingPosition:
            break

    if kingPosition is not None:
        corners = [(0, 0), (0, board.size - 1), (board.size - 1, 0), (board.size - 1, board.size - 1)]
        nearestCorner = min(corners, key=lambda c: abs(kingPosition[0] - c[0]) + abs(kingPosition[1] - c[1]))
        manhattanDistance = abs(kingPosition[0] - nearestCorner[0]) + abs(kingPosition[1] - nearestCorner[1])
        if aiPlayer == "D":
            score -= (manhattanDistance * KING_DISTANCE_WEIGHT)
        else:
            score += (manhattanDistance * KING_DISTANCE_WEIGHT)
    return score    

def alphaBeta(board, depth, alpha, beta, isMaximizing, currentTurn, aiPlayer):
    if depth == 0 or check_winner(board) is not None:
        return evaluate(board, aiPlayer)
    legalMoves = get_legal_moves(board, currentTurn)
    nextTurn = "D" if currentTurn == "A" else "A"
    if isMaximizing:
        maxEval = -float('inf')
        for move in legalMoves:
            ((from_row, from_col), (to_row, to_col)) = move
            newBoard = clone_board(board)
            pieceToMove = board.grid[from_row][from_col]
            newBoard.move(from_row, from_col, to_row, to_col, pieceToMove)
            apply_captures(newBoard, (to_row, to_col), currentTurn)
            eval = alphaBeta(newBoard, depth - 1, alpha, beta, False, nextTurn, aiPlayer)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float('inf')
        for move in legalMoves:
            ((from_row, from_col), (to_row, to_col)) = move
            newBoard = clone_board(board)
            pieceToMove = board.grid[from_row][from_col]
            newBoard.move(from_row, from_col, to_row, to_col, pieceToMove)
            apply_captures(newBoard, (to_row, to_col), currentTurn)
            eval = alphaBeta(newBoard, depth - 1, alpha, beta, True, nextTurn, aiPlayer)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval

def get_best_move(board, player, depth):
    bestMove = None
    bestScore = -float('inf')
    legalMoves = get_legal_moves(board, player)
    nextTurn = "D" if player == "A" else "A"
    for move in legalMoves:
        ((from_row, from_col), (to_row, to_col)) = move
        newBoard = clone_board(board)
        pieceToMove = board.grid[from_row][from_col]
        newBoard.move(from_row, from_col, to_row, to_col, pieceToMove)
        apply_captures(newBoard, (to_row, to_col), player)
        eval = alphaBeta(newBoard, depth - 1, -float('inf'), float('inf'), False, nextTurn, player)
        if eval > bestScore:
            bestScore = eval
            bestMove = move
    return bestMove