"""
Starter Code for Assignment 1 - COMP 8085
Please do not redistribute this code our your solutions
The game engine to keep track of the game and provider of a generic AI implementation
 You need to extend the GenericAI class to perform a better job in searching for the next move!
"""
# pip install Chessnut
from hashlib import algorithms_available
import json
import math
import os
from tqdm import trange

from Chessnut import Game
from enum import Enum
import random
import time
from collections import deque


def create_generator(g_list):
	for num in g_list:
		yield num
	yield "done"


class GameResult(Enum):
	WON = 1
	LOST = 2
	STALEMATE = 3
	DRAWBY50M = 4


class AIEngine:
	def __init__(self, board_state, reasoning_depth=3):
		self.game = Game(board_state)
		self.computer = GenericAI(self.game, reasoning_depth)
		self.leaderboard = {"White": {"Wins": 0, "Loses": 0, "Draws": 0}, "Black": {"Wins": 0, "Loses": 0, "Draws": 0}}

	def prompt_user(self):
		"""
		Use this function to play with the ai bot created in the constructor
		"""
		self.computer.print_board(str(self.game))
		fifty_move_draw = False
		playing_side = "White"
		try:
			while self.game.status < 2 and not fifty_move_draw:
				playing_side = "White"
				user_move = input("\nMake a move: \033[95m")
				print("\033[0m")
				while user_move not in self.game.get_moves() and user_move != "ff":
					user_move = input("Please enter a valid move: ")
				if user_move == "ff":
					print("Execution Stopped!")
					break
				self.game.apply_move(user_move)
				fifty_move_draw = self.check_fifty_move_draw()
				captured = self.captured_pieces(str(self.game))
				start_time = time.time()
				self.computer.print_board(str(self.game), captured)
				print("\nComputer Playing...\n")
				if self.game.status < 2 and not fifty_move_draw:
					playing_side = "Black"
					current_state = str(self.game)
					computer_move = self.computer.make_move(current_state)
					piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
					start = computer_move[:2]
					end = computer_move[2:4]
					piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2]))]
					captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
					if captured_piece != " ":
						captured_piece = piece_name[captured_piece.lower()]
						print("---------------------------------")
						print("Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
							  "at \033[91m{end}\033[0m.".format(piece=piece, start=start, captured_piece=captured_piece, end=end))
						print("---------------------------------")
					else:
						print("---------------------------------")
						print("Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
							piece=piece, start=start, end=end))
						print("---------------------------------")
					print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.node_count))
					print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
					self.game.apply_move(computer_move)
					fifty_move_draw = self.check_fifty_move_draw()
				captured = self.captured_pieces(str(self.game))
				self.computer.print_board(str(self.game), captured)
			self.record_winner(self.computer, "Black", playing_side, fifty_move_draw)
			print("Game Ended!")
		except KeyboardInterrupt:
			print("Execution Stopped!")


	def play_with_mcts(self):
		"""
		Use this function to play with the ai bot created in the constructor
		"""
		self.computer = MCTSAI(self.game)
		self.computer.print_board(str(self.game))
		fifty_move_draw = False
		playing_side = "White"
		try:
			while self.game.status < 2 and not fifty_move_draw:
				playing_side = "White"
				user_move = input("\nMake a move: \033[95m")
				print("\033[0m")
				while user_move not in self.game.get_moves() and user_move != "ff":
					user_move = input("Please enter a valid move: ")
				if user_move == "ff":
					print("Execution Stopped!")
					break
				self.game.apply_move(user_move)
				fifty_move_draw = self.check_fifty_move_draw()
				captured = self.captured_pieces(str(self.game))
				start_time = time.time()
				self.computer.print_board(str(self.game), captured)
				print("\nComputer Playing...\n")
				if self.game.status < 2 and not fifty_move_draw:
					playing_side = "Black"
					current_state = str(self.game)
					computer_move = self.computer.make_move(current_state)
					piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
					start = computer_move[:2]
					end = computer_move[2:4]
					piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2]))]
					captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
					if captured_piece != " ":
						captured_piece = piece_name[captured_piece.lower()]
						print("---------------------------------")
						print("Computer's \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
							  "at \033[91m{end}\033[0m.".format(piece=piece, start=start, captured_piece=captured_piece, end=end))
						print("---------------------------------")
					else:
						print("---------------------------------")
						print("Computer moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
							piece=piece, start=start, end=end))
						print("---------------------------------")
					print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.node_count))
					print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
					self.game.apply_move(computer_move)
					fifty_move_draw = self.check_fifty_move_draw()
				captured = self.captured_pieces(str(self.game))
				self.computer.print_board(str(self.game), captured)
			self.record_winner(self.computer, "Black", playing_side, fifty_move_draw)
			print("Game Ended!")
		except KeyboardInterrupt:
			print("Execution Stopped!")


	def record_winner(self, ai_bot, bot_side, losing_side, fifty_move_draw):
		print("\nGame result for {}:".format(bot_side))
		if fifty_move_draw:
			ai_bot.record_winner(GameResult.DRAWBY50M)
			self.leaderboard[bot_side]["Draws"] += 1
		elif self.game.status == 3:
			ai_bot.record_winner(GameResult.STALEMATE)
			self.leaderboard[bot_side]["Draws"] += 1
		elif self.game.status == 2 and losing_side == bot_side:
			ai_bot.record_winner(GameResult.LOST)
			self.leaderboard[bot_side]["Loses"] += 1
		elif self.game.status == 2 and losing_side != bot_side:
			ai_bot.record_winner(GameResult.WON)
			self.leaderboard[bot_side]["Wins"] += 1
		else:
			raise ValueError("Should not happen!")

	def clear_leaderboard(self):
		self.leaderboard = {"White": {"Wins": 0, "Loses": 0, "Draws": 0}, "Black": {"Wins": 0, "Loses": 0, "Draws": 0}}

	def check_fifty_move_draw(self):
		return int(str(self.game).split()[4]) > 100

	def play_with_self_MinimaxAI(self):
		"""
		# ############################################################################################################################
		# ### MINI MAX (ALPHA-BETA PRUNING)
		# ### https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
		# ############################################################################################################################
		"""
		self.game = Game('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
		self.computer = {"White": GenericAI(self.game, 2), "Black": MinimaxAI(self.game, 2)}
		self.computer["White"].print_board(str(self.game))
		bot_side = "White"
		fifty_move_draw = False
		while self.game.status < 2 and not fifty_move_draw:
			start_time = time.time()
			computer_move = self.computer[bot_side].make_move(str(self.game))
			piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
			start = computer_move[:2]
			end = computer_move[2:4]
			piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2])).lower()]
			captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
			if captured_piece != " ":
				captured_piece = piece_name[captured_piece.lower()]
				print("---------------------------------")
				print("{bot_side}'s \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
					  "at \033[91m{end}\033[0m.".format(bot_side=bot_side, piece=piece, start=start, captured_piece=captured_piece, end=end))
				print("---------------------------------")
			else:
				print("---------------------------------")
				print("{bot_side} moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
					bot_side=bot_side, piece=piece, start=start, end=end))
				print("---------------------------------")
			print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer[bot_side].node_count))
			print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
			print(str(self.game))
			self.game.apply_move(computer_move)
			fifty_move_draw = self.check_fifty_move_draw()
			captured = self.captured_pieces(str(self.game))
			self.computer[bot_side].print_board(str(self.game), captured)
			bot_side = "Black" if bot_side == "White" else "White"
		self.record_winner(self.computer["White"], "White", bot_side, fifty_move_draw)
		self.record_winner(self.computer["Black"], "Black", bot_side, fifty_move_draw)
		print("Game Ended!")
		# convert self.leaderboard dict to single line string
		leaderboard_string = ""
		# write the leader board to a minimax_vs_generic.txt file
		with open("minimax_vs_generic.txt", "a") as f:
			f.write(str(self.leaderboard))
			f.write("\n")

	def play_with_self_IterativeDeepeningAI(self):
		"""
		# ############################################################################################################################
		# ### Iterative Deepening AI
		# ### https://en.wikipedia.org/wiki/Iterative_deepening
		# ############################################################################################################################
		"""
		self.game = Game('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
		self.computer = {"White": MinimaxAI(self.game, 2), "Black": IterativeDeepeningAI(self.game, 4)}
		self.computer["White"].print_board(str(self.game))
		bot_side = "White"
		fifty_move_draw = False
		while self.game.status < 2 and not fifty_move_draw:
			start_time = time.time()
			computer_move = self.computer[bot_side].make_move(str(self.game))
			piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
			start = computer_move[:2]
			end = computer_move[2:4]
			piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2])).lower()]
			captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
			if captured_piece != " ":
				captured_piece = piece_name[captured_piece.lower()]
				print("---------------------------------")
				print("{bot_side}'s \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
					  "at \033[91m{end}\033[0m.".format(bot_side=bot_side, piece=piece, start=start, captured_piece=captured_piece, end=end))
				print("---------------------------------")
			else:
				print("---------------------------------")
				print("{bot_side} moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
					bot_side=bot_side, piece=piece, start=start, end=end))
				print("---------------------------------")
			print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer[bot_side].node_count))
			print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
			print(str(self.game))
			self.game.apply_move(computer_move)
			fifty_move_draw = self.check_fifty_move_draw()
			captured = self.captured_pieces(str(self.game))
			self.computer[bot_side].print_board(str(self.game), captured)
			bot_side = "Black" if bot_side == "White" else "White"
		self.record_winner(self.computer["White"], "White", bot_side, fifty_move_draw)
		self.record_winner(self.computer["Black"], "Black", bot_side, fifty_move_draw)
		print("Game Ended!")
		# write the leader board to a iterativedeepening_vs_iterativedeepening.txt file
		with open("iterativedeepening_vs_minimax.txt.txt", "a") as f:
			f.write(str(self.leaderboard))
			f.write("\n")


	def play_with_self_MCTSAI(self):
		"""
		# ############################################################################################################################
		# ### Monte Carlo AI
		# ### https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
		# ############################################################################################################################
		"""
		self.game = Game('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
		self.computer = {"White": MCTSAI(self.game, 2), "Black": MCTSAI(self.game, 2)}
		self.computer["White"].print_board(str(self.game))
		bot_side = "White"
		fifty_move_draw = False
		while self.game.status < 2 and not fifty_move_draw:
			start_time = time.time()
			computer_move = self.computer[bot_side].make_move(str(self.game))
			piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
			start = computer_move[:2]
			end = computer_move[2:4]
			piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2])).lower()]
			captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
			if captured_piece != " ":
				captured_piece = piece_name[captured_piece.lower()]
				print("---------------------------------")
				print("{bot_side}'s \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
					  "at \033[91m{end}\033[0m.".format(bot_side=bot_side, piece=piece, start=start, captured_piece=captured_piece, end=end))
				print("---------------------------------")
			else:
				print("---------------------------------")
				print("{bot_side} moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
					bot_side=bot_side, piece=piece, start=start, end=end))
				print("---------------------------------")
			print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer[bot_side].node_count))
			print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
			print(str(self.game))
			self.game.apply_move(computer_move)
			fifty_move_draw = self.check_fifty_move_draw()
			captured = self.captured_pieces(str(self.game))
			self.computer[bot_side].print_board(str(self.game), captured)
			bot_side = "Black" if bot_side == "White" else "White"
		self.record_winner(self.computer["White"], "White", bot_side, fifty_move_draw)
		self.record_winner(self.computer["Black"], "Black", bot_side, fifty_move_draw)
		print("Game Ended!")
		# write the leader board to a MCTSAI_vs_MCTSAI.txt file
		with open("mcts.model", "a") as f:
			f.write(str(self.leaderboard))
			f.write("\n")

	def play_with_self(self):
		"""
		Use this function to have two different AI bots play with each other and see their game
		"""
		self.game = Game('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
		self.computer = {"White": GenericAI(self.game, 2), "Black": GenericAI(self.game, 2)}
		self.computer["White"].print_board(str(self.game))
		bot_side = "White"
		fifty_move_draw = False
		while self.game.status < 2 and not fifty_move_draw:
			start_time = time.time()
			computer_move = self.computer[bot_side].make_move(str(self.game))
			piece_name = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
			start = computer_move[:2]
			end = computer_move[2:4]
			piece = piece_name[self.game.board.get_piece(self.game.xy2i(computer_move[:2])).lower()]
			captured_piece = self.game.board.get_piece(self.game.xy2i(computer_move[2:4]))
			if captured_piece != " ":
				captured_piece = piece_name[captured_piece.lower()]
				print("---------------------------------")
				print("{bot_side}'s \033[92m{piece}\033[0m at \033[92m{start}\033[0m captured \033[91m{captured_piece}\033[0m "
					  "at \033[91m{end}\033[0m.".format(bot_side=bot_side, piece=piece, start=start, captured_piece=captured_piece, end=end))
				print("---------------------------------")
			else:
				print("---------------------------------")
				print("{bot_side} moved \033[92m{piece}\033[0m at \033[92m{start}\033[0m to \033[92m{end}\033[0m.".format(
					bot_side=bot_side, piece=piece, start=start, end=end))
				print("---------------------------------")
			print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer[bot_side].node_count))
			print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
			print(str(self.game))
			self.game.apply_move(computer_move)
			fifty_move_draw = self.check_fifty_move_draw()
			captured = self.captured_pieces(str(self.game))
			self.computer[bot_side].print_board(str(self.game), captured)
			bot_side = "Black" if bot_side == "White" else "White"
		self.record_winner(self.computer["White"], "White", bot_side, fifty_move_draw)
		self.record_winner(self.computer["Black"], "Black", bot_side, fifty_move_draw)
		print("Game Ended!")

	def play_with_self_non_verbose(self):
		"""
		Use this function to have two different AI bots play with each other without printing the game board or the decisions they make in the console.
		"""
		self.game = Game('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
		self.computer = {"White": GenericAI(self.game, 2), "Black": GenericAI(self.game, 2)}
		bot_side = "White"
		fifty_move_draw = False
		while self.game.status < 2 and not fifty_move_draw:
			computer_move = self.computer[bot_side].make_move(str(self.game))
			self.game.apply_move(computer_move)
			fifty_move_draw = self.check_fifty_move_draw()
			bot_side = "Black" if bot_side == "White" else "White"
		self.record_winner(self.computer["White"], "White", bot_side, fifty_move_draw)
		self.record_winner(self.computer["Black"], "Black", bot_side, fifty_move_draw)

	@staticmethod
	def captured_pieces(board_state):
		piece_tracker = {'P': 8, 'B': 2, 'N': 2, 'R': 2, 'Q': 1, 'K': 1, 'p': 8, 'b': 2, 'n': 2, 'r': 2, 'q': 1, 'k': 1}
		captured = {"w": [], "b": []}
		for char in board_state.split()[0]:
			if char in piece_tracker:
				piece_tracker[char] -= 1
		for piece in piece_tracker:
			if piece_tracker[piece] > 0:
				if piece.isupper():
					captured['w'] += piece_tracker[piece] * piece
				else:
					captured['b'] += piece_tracker[piece] * piece
			piece_tracker[piece] = 0
		return captured


class BoardNode:
	def __init__(self, board_state=None, algebraic_move=None, value=None):
		self.board_state = board_state
		self.algebraic_move = algebraic_move
		self.value = value


class GenericAI:
	def __init__(self, game, max_depth=4, leaf_nodes=None, node_count=0):
		if leaf_nodes is None:
			leaf_nodes = []
		self.max_depth = max_depth
		self.leaf_nodes = create_generator(leaf_nodes)
		self.game = game
		self.node_count = node_count

	@property
	def name(self):
		return "Dumb AI"

	def get_moves(self, board_state=None):
		if board_state is None:
			board_state = str(self.game)
		possible_moves = []
		for move in Game(board_state).get_moves():
			if len(move) < 5 or move[4] == "q":
				clone = Game(board_state)
				clone.apply_move(move)
				node = BoardNode(str(clone))
				node.algebraic_move = move
				possible_moves.append(node)
		return possible_moves

	def make_move(self, board_state):
		possible_moves = self.get_moves(board_state)
		# TODO use search algorithms to find the best move in here

		# ############################################################################################################################
		# ### MINI MAX (ALPHA-BETA PRUNING)
		# ### https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
		# ############################################################################################################################
		# ## get the mimimax class to use
		# minimax = MinimaxAI(self.game, self.max_depth, self.leaf_nodes, self.node_count)
		# ##  get best move from minimax algorithm
		# best_move = minimax.make_move(board_state)


		# ############################################################################################################################
		# ### Iterative Deepening AI
		# ### https://en.wikipedia.org/wiki/Iterative_deepening
		# ############################################################################################################################
		# ## get the iterative deepening class to use
		# ids = IterativeDeepeningAI(self.game, self.max_depth, self.leaf_nodes, self.node_count)
		# ##  get best move from iterative deepening algorithm
		# best_move = ids.make_move(board_state)


		# ############################################################################################################################
		# ### Monte Carlo AI
		# ### https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
		# ############################################################################################################################
		# ## get the monte carlo class to use
		# mcts = MCTSAI(self.game, self.max_depth, self.leaf_nodes, self.node_count)
		# ##  get best move from monte carlo algorithm
		# best_move = mcts.make_move(board_state)


		best_move = random.choice(possible_moves)
		print("BEST MOVE : ",best_move.algebraic_move)

		return best_move.algebraic_move

	def record_winner(self, result):
		print("The game result: {}".format(result.name))

	def print_board(self, board_state, captured=None):
		if captured is None:
			captured = {"w": [], "b": []}
		piece_symbols = {'p': '♟', 'b': '♝', 'n': '♞', 'r': '♜', 'q': '♛', 'k': '♚', 'P': '\033[36m\033[1m♙\033[0m',
						 'B': '\033[36m\033[1m♗\033[0m', 'N': '\033[36m\033[1m♘\033[0m', 'R': '\033[36m\033[1m♖\033[0m',
						 'Q': '\033[36m\033[1m♕\033[0m', 'K': '\033[36m\033[1m♔\033[0m'}
		board_state = board_state.split()[0].split("/")
		board_state_str = "\n"
		white_captured = " ".join(piece_symbols[piece] for piece in captured['w'])
		black_captured = " ".join(piece_symbols[piece] for piece in captured['b'])
		for i, row in enumerate(board_state):
			board_state_str += str(8 - i)
			for char in row:
				if char.isdigit():
					board_state_str += " ♢" * int(char)
				else:
					board_state_str += " " + piece_symbols[char]
			if i == 0:
				board_state_str += "   Captured:" if len(white_captured) > 0 else ""
			if i == 1:
				board_state_str += "   " + white_captured
			if i == 6:
				board_state_str += "   Captured:" if len(black_captured) > 0 else ""
			if i == 7:
				board_state_str += "   " + black_captured
			board_state_str += "\n"
		board_state_str += "  A B C D E F G H"
		self.node_count = 0
		print(board_state_str)


class MinimaxAI(GenericAI):
	def __init__(self, game, max_depth=4, leaf_nodes=None, node_count=0):
		super(MinimaxAI, self).__init__(game, max_depth, leaf_nodes, node_count)
		self.cache = {}
		self.found_in_cache = 0

	@property
	def name(self):
		return "Minimax AI"

	def make_move(self, board_state):
		# TODO re-write this code to use minimax function to pick the best move
		## use minimax to pick the best move
		possible_moves = self.get_moves(board_state)
		alpha = float("-inf") # lower bound
		beta = float("inf") # TODO change this to a more reasonable value
		best_move = possible_moves[0]
		for move in possible_moves:
			board_value = self.minimax(move, alpha, beta, 1) # 1 is max depth for minimax
			if alpha < board_value: # if the value is greater than the current alpha, update the alpha and the best move
				alpha = board_value # update alpha
				best_move = move # TODO change this to be a list of moves
				best_move.value = alpha # set the value of the move
		# return the best move
		return best_move.algebraic_move


	def minimax(self, node, alpha, beta, current_depth=0):
		# TODO implement this function
		current_depth += 1
		if current_depth == self.max_depth:
			board_value = self.get_heuristic(node.board_state)
			if current_depth % 2 == 0:
				if (alpha < board_value):
					alpha = board_value
				self.node_count += 1
				return alpha
			else: #
				if (beta > board_value):
					beta = board_value
				self.node_count += 1
				return beta
		if current_depth % 2 == 0:
			# MINIMIZING NODE
			for child_node in self.get_moves(node.board_state):
				if alpha < beta:
					board_value = self.minimax(child_node,alpha, beta, current_depth)
					if beta > board_value:
						beta = board_value
			return beta
		else:
			# MAXIMISING NODE
			for child_node in self.get_moves(node.board_state):
				if alpha < beta:
					board_value = self.minimax(child_node,alpha, beta, current_depth)
					if alpha < board_value:
						alpha = board_value
			return alpha

	def get_heuristic(self, board_state=None):
		curr_board_state_cache = board_state.split(" ")[0] + " " + board_state.split(" ")[1]
		if board_state is None:
			board_state = str(self.game)
		if curr_board_state_cache in self.cache:
			self.found_in_cache += 1
			return self.cache[curr_board_state_cache]
		clone = Game(board_state)
		pnts = 0 # points for the current player

		piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0} # piece values

		# get the current player
		curr_plyer = board_state.split(" ")[1]

		if curr_plyer== 'w':
			for piece in board_state.split(" ")[0]:
				if piece.islower():
					pnts += piece_values[piece] # black pieces
				elif piece.isupper():
					pnts -= piece_values[piece.lower()] # negative value for white pieces
		if curr_plyer== 'b':
			for piece in board_state.split(" ")[0]:
				if piece.isupper():
					pnts += piece_values[piece.lower()]
				elif piece.islower():
					pnts -= piece_values[piece.lower()]


		pnts = pnts * 100 # multiply by 100 to make it easier to compare
		
		## check if in check
		stat = clone.status # check if in check
		player_now = board_state.split(" ")[1]
		if stat == '1' and player_now!=curr_plyer:
			pnts += 1000
		elif stat == '2' and player_now!=curr_plyer:
			pnts += 2000
		elif stat == '1' and player_now==curr_plyer:
			pnts -= 1000
		elif stat == '2' and player_now==curr_plyer:
			pnts -= 2000

		# add randomness to the score
		pnts += random.randint(-10, 10)


		self.cache[curr_board_state_cache] = pnts # add to cache
		return pnts * 100




# TODO use the example of MinimaxAI class definition to prepare other AI bot search algorithms
class Graph():
	def __init__(self):
		self.nodes = []
		self.edges = []

	def add_node(self, node):
		self.nodes.append(node)

	def add_edge(self, node1, node2):
		self.edges.append((node1, node2))

	def get_node(self, node_id):
		for node in self.nodes:
			if node.id == node_id:
				return node
		return None

	def get_children(self, node):
		children = []
		for edge in self.edges:
			if edge[0] == node:
				children.append(edge[1])
		return children





class IterativeDeepeningAI(GenericAI):
	def __init__(self, game, max_depth=4, leaf_nodes=None, node_count=0):
		super(IterativeDeepeningAI, self).__init__(game, max_depth, leaf_nodes, node_count)
		self.cache = {}
		self.found_in_cache = 0

	@property
	def name(self):
		return "IterativeDeepening AI"

	def make_move(self, board_state):
		possible_moves = self.get_moves(board_state)

		## get best move from iterative deepening
		possible_moves = self.get_moves(board_state)
		alpha = float("-inf") # lower bound
		beta = float("inf") # TODO change this to a more reasonable value
		best_move = possible_moves[0]
		for move in possible_moves:
			board_value = self.ids(move, alpha, beta, 1) # 1 is the current depth
			if alpha < board_value: # if the value is greater than the current alpha, update the alpha and the best move
				alpha = board_value # update alpha
				best_move = move # TODO change this to be a list of moves
				best_move.value = alpha # set the value of the move
		# return the best move
		return best_move.algebraic_move

	def ids(self, node, alpha, beta, current_depth=0):
		# TODO implement this function
		current_depth += 1 # increment the depth
		if current_depth == self.max_depth:
			board_value = self.get_heuristic(node.board_state)
			if current_depth % 2 == 0:
				if (alpha < board_value):
					alpha = board_value
				self.node_count += 1
				return alpha
			else: #
				if (beta > board_value):
					beta = board_value
				self.node_count += 1
				return beta
		if current_depth % 2 == 0:
			# MINIMIZING NODE
			for child_node in self.get_moves(node.board_state):
				if alpha < beta:
					board_value = self.ids(child_node,alpha, beta, current_depth)
					if beta > board_value:
						beta = board_value
			return beta
		else:
			# MAXIMISING NODE
			for child_node in self.get_moves(node.board_state):
				if alpha < beta:
					board_value = self.ids(child_node,alpha, beta, current_depth)
					if alpha < board_value:
						alpha = board_value
			return alpha

	def get_heuristic(self, board_state=None):
		curr_board_state_cache = board_state.split(" ")[0] + " " + board_state.split(" ")[1]
		if board_state is None:
			board_state = str(self.game)
		if curr_board_state_cache in self.cache:
			self.found_in_cache += 1
			return self.cache[curr_board_state_cache]
		clone = Game(board_state)
		pnts = 0 # points for the current player

		piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0} # piece values

		# get the current player
		curr_plyer = board_state.split(" ")[1]

		if curr_plyer== 'w':
			for piece in board_state.split(" ")[0]:
				if piece.islower():
					pnts += piece_values[piece] # black pieces
				elif piece.isupper():
					pnts -= piece_values[piece.lower()] # negative value for white pieces
		if curr_plyer== 'b':
			for piece in board_state.split(" ")[0]:
				if piece.isupper():
					pnts += piece_values[piece.lower()]
				elif piece.islower():
					pnts -= piece_values[piece.lower()]


		pnts = pnts * 100 # multiply by 100 to make it easier to compare
		
		## check if in check
		stat = clone.status # check if in check
		player_now = board_state.split(" ")[1]
		if stat == '1' and player_now!=curr_plyer:
			pnts += 1000
		elif stat == '2' and player_now!=curr_plyer:
			pnts += 2000
		elif stat == '1' and player_now==curr_plyer:
			pnts -= 1000
		elif stat == '2' and player_now==curr_plyer:
			pnts -= 2000

		# add randomness to the score
		pnts += random.randint(-10, 10)


		self.cache[curr_board_state_cache] = pnts # add to cache
		return pnts * 100


class MCTSAI(GenericAI):
	def __init__(self, game, max_depth=4, leaf_nodes=None, node_count=0):
		super(MCTSAI, self).__init__(game, max_depth, leaf_nodes, node_count)
		self.cache = {}
		self.found_in_cache = 0

	@property
	def name(self):
		return "MCTS AI"

	## GEt the best move from the Monte Carlo Search Tree
	def make_move(self, board_state):
		possible_moves = self.get_moves(board_state)
		best_move = possible_moves[0]
		best_value =0

		## do a monte carlo search for all possible moves
		## evry possible move is evaluated against 100 plays witha random move generator
		sum_list = []

		for move in possible_moves:

			# clone board
			clone = Game(board_state)

			curr_plyer = str(clone).split(" ")[1] # get the current player

			# make the move
			clone.apply_move(move.algebraic_move)



			sums =0

			# create a second clone
			clone2 = Game(str(clone))
			for i in range(20):


				# get board state
				board_state2 = str(clone2)
				# get possible moves
				possible_moves2 = self.get_moves(board_state2)

				try:
					# make a random move for the second clone with the opposite player
					clone2.apply_move(random.choice(possible_moves2).algebraic_move)
					# eva;uate the move
					val = self.get_heuristic(str(clone2))

					sums += val # add the value to the sum
				except:
					pass

			sum_list.append(sums) # add the value to the list

		# get the highest iindex
		max_index = sum_list.index(max(sum_list))

		# print(sum_list,max_index)

		# get the move with the highest value
		best_move = possible_moves[max_index]



		# return the best move
		return best_move.algebraic_move


	def get_heuristic(self, board_state=None):
		curr_board_state_cache = board_state.split(" ")[0] + " " + board_state.split(" ")[1]
		if board_state is None:
			board_state = str(self.game)
		if curr_board_state_cache in self.cache:
			self.found_in_cache += 1
			return self.cache[curr_board_state_cache]
		clone = Game(board_state)
		black_pnts = 0 # points for the black player
		white_pnts = 0 # points for the white player

		piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0} # piece values

		for piece in board_state.split(" ")[0]:
			if piece.islower():
				black_pnts += piece_values[piece] # black pieces
			elif piece.isupper():
				white_pnts += piece_values[piece.lower()] # negative value for white pieces

		curr_plyer = str(clone).split(" ")[1] # get the current player




		## check if black is in check
		stat = clone.status # check if in check
		if (curr_plyer == 'b' and stat == 1):
			black_pnts -= 100 # black is in check
		elif (curr_plyer == 'b' and stat == 2):
			black_pnts -= 1000 # black is in checkmate

		## check if white is in check
		stat = clone.status # check if in check
		if (curr_plyer != 'b' and curr_plyer == 'w' and stat == 1):
			white_pnts -= 100
		elif (curr_plyer != 'b' and curr_plyer == 'w' and stat == 2):
			white_pnts -= 1000



		# add randomness to the score
		# pnts += random.randint(-10, 10)


		if curr_plyer == 'b':
			pnts = black_pnts - white_pnts # black is the current player
		else:
			pnts = white_pnts - black_pnts # get the difference

		pnts = pnts * 100 # multiply by 100


		self.cache[curr_board_state_cache] = pnts # add to cache
		return pnts * 100





if __name__ == '__main__':
	
	# test_engine.prompt_user()

	# test_engine = AIEngine('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
	# test_engine.clear_leaderboard()
	# for i in range(30):
	# 	test_engine.play_with_self_MinimaxAI()

	# test_engine = AIEngine('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
	# test_engine.clear_leaderboard()
	# for i in range(30):
	# 	test_engine.play_with_self_IterativeDeepeningAI()

	test_engine = AIEngine('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
	test_engine.clear_leaderboard()
	for i in range(30):
		test_engine.play_with_self_MCTSAI()

	# test_engine = AIEngine('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
	# test_engine.clear_leaderboard()
	# test_engine .play_with_mcts()
