import numpy as np
import random
import pygame
import sys
import math
import time
import pprint
import random

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
	boards = [np.zeros((ROW_COUNT,COLUMN_COUNT)), np.zeros((ROW_COUNT,COLUMN_COUNT)), np.zeros((ROW_COUNT,COLUMN_COUNT)), np.zeros((ROW_COUNT,COLUMN_COUNT))]
	return boards
	# board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	# return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True

        # Check positively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True

        # Check negatively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(3, ROW_COUNT):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(boards):
    for board in boards:
        if winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0:
            return True

def minimax(boards, depth, alpha, beta, maximizingPlayer):
    valid_actions = []
    for board in boards:
        valid_locations += get_valid_locations(board)
        valid_actions.append(valid_locations)
        is_terminal = is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if winning_move(board, AI_PIECE):
                    return (None, 100000000000000)
                elif winning_move(board, PLAYER_PIECE):
                    return (None, -10000000000000)
                else: # Game is over, no more valid moves
                    return (None, 0)
            else: # Depth is zero
                return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):
	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

boards = create_board()
game_over = False
# turn = random.randint(PLAYER, AI)
turn = PLAYER

while not game_over:
    for board in boards:
        print_board(board)
        print('===========================================')

    if turn == AI and not game_over:
        #col = random.randint(0, COLUMN_COUNT-1)
        #col = pick_best_move(board, AI_PIECE)
        col, minimax_score = minimax(boards, 5, -math.inf, math.inf, True)
        if is_valid_location(board, col):
            #pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                game_over = True
                print('AI WINS!!!')

            turn += 1
            turn = turn % 2
            
    if turn == PLAYER and not game_over:
        idx = int(input('Please choose a board (0-3): '))
        col = int(input('Please choose a column (0-6): '))
        othr_boards = [0,1,2,3]
        othr_boards.remove(col)
        if not (isinstance(idx, int) and idx >= 0 and idx <= 3):
            print('Please enter a valid board number between 0-3 inclusivley')
        elif not (isinstance(idx, int) and col >= 0 and col <= 6):
            print('Please enter a valid column number between 0-6 inclusivley')
        elif is_valid_location(boards[idx], col):
            for i in range(0, len(othr_boards)):
                valid_actions = get_valid_locations(boards[othr_boards[i]]) #Get valid columns
                print(valid_actions)
                rand_col = random.choice(valid_actions) #Pick a random column
                row = get_next_open_row(boards[othr_boards[i]], rand_col)
                drop_piece(boards[othr_boards[i]], row, rand_col, PLAYER_PIECE)
            row = get_next_open_row(boards[idx], col)
            drop_piece(boards[idx], row, col, PLAYER_PIECE)
            if winning_move(boards[idx], PLAYER_PIECE):
                game_over = True
                print('PLAYER WINS!!!!')

            # turn += 1
            # turn = turn % 2
        
    if game_over:
        pygame.time.wait(3000)