# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time

class Game:
	MINIMAX = 0
	ALPHABETA = 1
	HUMAN = 2
	AI = 3
	
	def __init__(self, recommend = True, n=3, b=0):
		self.initialize_game(n)
		self.recommend = recommend
		
	def initialize_game(self, n):
		self.current_state = [['.' for i in range(n)] for j in range(n)]
		# Player X or 1 always plays first
		self.player_turn = 'X'

	def draw_board(self, size=3):
		print()
		for y in range(0, size):
			for x in range(0, size):
				print(F'{self.current_state[x][y]}', end="")
			print()
		print()
		
	def is_valid(self, px, py, n):
		if px < 0 or px > n or py < 0 or py > n:
			return False
		elif self.current_state[px][py] != '.':
			return False
		else:
			return True

	def is_end(self, n, s):
		winStringX = 'X'*s
		winStringO = 'O'*s
		# Vertical win
		transposedArray = [list(i) for i in zip(*self.current_state)]
		for i in range(0, n):
			verticalString = ""
			for j in range(0, n):
				verticalString = verticalString + transposedArray[i][j]
			if (winStringX in verticalString):
				return 'X'
			elif (winStringO in verticalString):
				return 'O'
		# Horizontal win
		for i in range(0, n):
			horizontalString = ""
			for j in range(0, n):
				horizontalString = horizontalString + self.current_state[i][j]
			if (winStringX in horizontalString):
				return 'X'
			elif (winStringO in horizontalString):
				return 'O'
		# Diagonal win
		h, w = len(self.current_state), len(self.current_state[0])

		diagList = [[self.current_state[h - 1 - q][p - q]
				for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
			   for p in range(h + w - 1)]
		for i in range(0, len(diagList)):
			diagonalString = ""
			for j in range(0, len(diagList[i])):
				diagonalString = diagonalString + diagList[i][j]
			if (winStringX in diagonalString):
				return 'X'
			elif (winStringO in diagonalString):
				return 'O'

		antiDiagList = [[self.current_state[p - q][q]
		  for q in range(max(p - h + 1, 0), min(p + 1, w))]
		 for p in range(h + w - 1)]
		for i in range(0, len(antiDiagList)):
			diagonalString = ""
			for j in range(0, len(antiDiagList[i])):
				diagonalString = diagonalString + antiDiagList[i][j]
			if (winStringX in diagonalString):
				return 'X'
			elif (winStringO in diagonalString):
				return 'O'
		# Is whole board full?
		for i in range(0, n):
			for j in range(0, n):
				# There's an empty field, we continue the game
				if (self.current_state[i][j] == '.'):
					return None
		# It's a tie!
		return '.'

	def check_end(self, n, s):
		self.result = self.is_end(n, s)
		# Printing the appropriate message if the game has ended
		if self.result != None:
			if self.result == 'X':
				print('The winner is X!')
			elif self.result == 'O':
				print('The winner is O!')
			elif self.result == '.':
				print("It's a tie!")
			#self.initialize_game()
		return self.result

	def input_move(self):
		while True:
			print(F'Player {self.player_turn}, enter your move:')
			px = int(input('enter the x coordinate: '))
			py = int(input('enter the y coordinate: '))
			if self.is_valid(px, py):
				return (px,py)
			else:
				print('The move is not valid! You may try again.')

	def switch_player(self):
		if self.player_turn == 'X':
			self.player_turn = 'O'
		elif self.player_turn == 'O':
			self.player_turn = 'X'
		return self.player_turn

	def minimax(self, max=False, n=3, s=3, d=4, iter=0, startTime=0, t=10):
		# Minimizing for 'X' and maximizing for 'O'
		# Possible values are:
		# -1 - win for 'X'
		# 0  - a tie
		# 1  - loss for 'X'
		# We're initially setting it to 2 or -2 as worse than the worst case:
		value = 2
		if max:
			value = -2
		x = None
		y = None
		if iter > d:
			return (value, x, y)
		result = self.is_end(n, s)
		if result == 'X':
			return (-1, x, y)
		elif result == 'O':
			return (1, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, n):
			for j in range(0, n):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.minimax(max=False, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.minimax(max=True, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
					timeElapsed = time.time() - startTime
					if iter > d or timeElapsed >= t-(t*0.025):
						return (value, x, y)
		return (value, x, y)

	def alphabeta(self, alpha=-2, beta=2, max=False, n=3, s=3, d=4, iter=0, startTime=0, t=10):
		# Minimizing for 'X' and maximizing for 'O'
		# Possible values are:
		# -1 - win for 'X'
		# 0  - a tie
		# 1  - loss for 'X'
		# We're initially setting it to 2 or -2 as worse than the worst case:
		value = 2
		if max:
			value = -2
		x = None
		y = None
		result = self.is_end(n, s)
		if result == 'X':
			return (-1, x, y)
		elif result == 'O':
			return (1, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, n):
			for j in range(0, n):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.alphabeta(alpha, beta, max=False, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.alphabeta(alpha, beta, max=True, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
					timeElapsed = round(time.time() - startTime, 7)
					if iter > d or timeElapsed >= t-(t*0.025):
						return (value, x, y)
					if max: 
						if value >= beta:
							return (value, x, y)
						if value > alpha:
							alpha = value
					else:
						if value <= alpha:
							return (value, x, y)
						if value < beta:
							beta = value
		return (value, x, y)

	def play(self,algo=True,player_x=None,player_o=None,n=3,s=3,d1=4,d2=4,t=10):
		if algo == True:
			algo = self.ALPHABETA
		elif algo == False:
			algo = self.MINIMAX
		if player_x == None:
			player_x = self.HUMAN
		if player_o == None:
			player_o = self.HUMAN
		while True:
			self.draw_board(n)
			if self.check_end(n, s):
				return
			start = time.time()
			if algo == self.MINIMAX:
				if self.player_turn == 'X':
					(_, x, y) = self.minimax(max=False, n=n, s=s, d=d1, iter=0, startTime=start, t=t)
				else:
					(_, x, y) = self.minimax(max=True, n=n, s=s, d=d2, iter=0, startTime=start, t=t)
			else: # algo == self.ALPHABETA
				if self.player_turn == 'X':
					(m, x, y) = self.alphabeta(max=False, n=n, s=s, d=d1, iter=0, startTime=start, t=t)
				else:
					(m, x, y) = self.alphabeta(max=True, n=n, s=s, d=d2, iter=0, startTime=start, t=t)
			end = time.time()
			if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
					if self.recommend:
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Recommended move: x = {x}, y = {y}')
					(x,y) = self.input_move()
			if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
			self.current_state[x][y] = self.player_turn
			self.switch_player()

def receiveInputs():
	n = 0
	while n < 3 or n > 10:
		n = int(input("Enter size n of the board: "))
		if n < 3 or n > 10:
			print("n must be a value between 3 and 10! Please try again.")
	b = -1
	while b < 0 or b > 2*n:
		b = int(input("Enter the number b of the blocs: "))
		if b < 0 or b > 2*n:
			print("b must be a value between 0 and " + 2*n + "! Please try again.")
	s = 0
	while s < 3 or s > n:
		s = int(input("Enter the number s for the winning line-up size: "))
		if s < 3 or s > n:
			print("s must be a value between 3 and " + n + "! Please try again.")
	d1 = -1
	while d1 < 0:
		d1 = int(input("Enter the maximum depth of the adversarial search for player 1: "))
		if d1 < 0:
			print("d1 must be a value greater than 0! Please try again.")
	d2 = -1
	while d2 < 0:
		d2 = int(input("Enter the maximum depth of the adversarial search for player 2: "))
		if d2 < 0:
			print("d2 must be a value greater than 0! Please try again.")
	t = -1
	while t < 0:
		t = int(input("Enter the maximum allowed time (in seconds) for the program to return a move: "))
		if t < 0:
			print("t must be a value greater than 0! Please try again.")
	a = None
	ain = -1
	while ain != 0 and ain != 1:
		ain = int(input("Enter the choice between minimax (0) or alphabeta (1): "))
		if ain == 0:
			a = False
		elif ain == 1:
			a = True
		elif ain != 0 and ain != 1:
			print("Your input must be either 0 for minimax or 1 for alphabeta! Please try again.")
	player1 = None
	pin1 = -1
	while pin1 != 0 and pin1 != 1:
		pin1 = int(input("Should player 1 be human controlled? Enter 1 for yes, 0 for no: "))
		if pin1 == 0:
			player1 = Game.AI
		elif pin1 == 1:
			player1 = Game.HUMAN
		elif pin1 != 0 and pin1 != 1:
			print("Your input must be either 0 for no or 1 for yes! Please try again.")
	player2 = None
	pin2 = -1
	while pin2 != 0 and pin2 != 1:
		pin2 = int(input("Should player 1 be human controlled? Enter 1 for yes, 0 for no: "))
		if pin2 == 0:
			player2 = Game.AI
		elif pin2 == 1:
			player2 = Game.HUMAN
		elif pin2 != 0 and pin2 != 1:
			print("Your input must be either 0 for no or 1 for yes! Please try again.")
	return n, b, s, d1, d2, t, a, player1, player2

def main():
	n, b, s, d1, d2, t, a, player1, player2 = receiveInputs()
	if (a):
		algo = Game.MINIMAX
	else:
		algo = Game.ALPHABETA
	g = Game(recommend=True, n=n)
	g.play(algo=algo,player_x=player1,player_o=player2,n=n,s=s,d1=d1,d2=d2,t=t)

if __name__ == "__main__":
	main()

