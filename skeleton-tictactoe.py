# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python
import re
import time
import random
import itertools

class Game:
	MINIMAX = 0
	ALPHABETA = 1
	HUMAN = 2
	AI = 3
	E1 = 4
	E2 = 5
	
	def __init__(self, recommend = True, n=3, b=0):
		self.initialize_game(n)
		self.recommend = recommend
		
	def initialize_game(self, n):
		self.current_state = [['.' for i in range(n)] for j in range(n)]
		# Player X or 1 always plays first
		self.player_turn = 'X'

	def draw_board(self, size=3, moveNum=0):
		print()
		header = "  "
		topLine = " +"
		for i in range(size):
			header = header + chr(ord('A') + i)
			topLine = topLine + "-"
		header = "{0}  (move #{1})".format(header, moveNum)
		print(header)
		print(topLine)
		for y in range(0, size):
			print(F'{y}|', end="")
			for x in range(0, size):
				print(F'{self.current_state[x][y]}', end="")
			print()
		print()

	def convert_input_x(self, px):
		inputX = 0
		if px == "A":
			inputX = 0
		elif px == "B":
			inputX = 1
		elif px == "C":
			inputX = 2
		elif px == "D":
			inputX = 3
		elif px == "E":
			inputX = 4
		elif px == "F":
			inputX = 5
		elif px == "G":
			inputX = 6
		elif px == "H":
			inputX = 7
		elif px == "I":
			inputX = 8
		elif px == "J":
			inputX = 9
		else:
			inputX = -1
		return inputX

	def convert_x_to_input(self, x):
		return chr(ord('A') + x)
		
	def is_valid(self, px, py, n):
		if px < 0 or px > n-1 or py < 0 or py > n-1:
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

	def e1_heuristic(self, n=3, s=3):
		# Simple heuristic optimized for X
		# Lower value is better for X
		# Higher value is better for O
		value = 0
		# Vertical
		transposedArray = [list(i) for i in zip(*self.current_state)]
		for i in range(0, n):
			verticalString = ""
			for j in range(0, n):
				verticalString = verticalString + transposedArray[i][j]
			value = value - verticalString.count('X') + verticalString.count('O')
		# Horizontal
		for i in range(0, n):
			horizontalString = ""
			for j in range(0, n):
				horizontalString = horizontalString + self.current_state[i][j]
			value = value - horizontalString.count('X') + horizontalString.count('O')
		# Diagonal win
		h, w = len(self.current_state), len(self.current_state[0])

		diagList = [[self.current_state[h - 1 - q][p - q]
					 for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
					for p in range(h + w - 1)]
		for i in range(0, len(diagList)):
			diagonalString = ""
			for j in range(0, len(diagList[i])):
				diagonalString = diagonalString + diagList[i][j]
			if len(diagonalString) >= s:
				value = value - diagonalString.count('X') + diagonalString.count('O')

		antiDiagList = [[self.current_state[p - q][q]
						 for q in range(max(p - h + 1, 0), min(p + 1, w))]
						for p in range(h + w - 1)]
		for i in range(0, len(antiDiagList)):
			diagonalString = ""
			for j in range(0, len(antiDiagList[i])):
				diagonalString = diagonalString + antiDiagList[i][j]
			if len(diagonalString) >= s:
				value = value - diagonalString.count('X') + diagonalString.count('O')
		return value

	# helper functions for e2
	def listOfCloseToWinning(self, maxLength=3, winningString='XX'):
		listOfClose = []
		for i in range(maxLength + 1):
			combination = winningString.rjust(i, '.')
			combination = combination.ljust(maxLength, '.')
			if len(combination) <= maxLength and combination not in listOfClose:
				listOfClose.append(combination)
		return listOfClose


	def e2_heuristic(self, n=3, s=3):
		# Slightly more complex heuristic, biased on defensive
		# Lower value is better for X
		# Higher value is better for O
		winningStringX = 'X'*(s-2)
		closeToWinX = self.listOfCloseToWinning(maxLength=s,winningString=winningStringX)
		winningStringO = 'O'*(s-2)
		closeToWinO = self.listOfCloseToWinning(maxLength=s,winningString=winningStringO)
		denialOChars = 'X'*(s-1) + 'O'
		denialXChars = 'X'*(s-1) + 'X'
		denialO = list(set(''.join(p) for p in itertools.permutations(denialOChars)))
		denialX = list(set(''.join(p) for p in itertools.permutations(denialXChars)))
		value = 0
		# Vertical
		transposedArray = [list(i) for i in zip(*self.current_state)]
		for i in range(0, n):
			verticalString = ""
			for j in range(0, n):
				verticalString = verticalString + transposedArray[i][j]
			if verticalString in closeToWinX:
				value = value - 15
			if verticalString in closeToWinO:
				value = value + 15
			for den in denialX:
				if den in verticalString:
					value = value - 35
			for den in denialO:
				if den in verticalString:
					value = value + 35
			if len(verticalString) > 0:
				consecutiveX = 0
				consecutiveY = 0
				if 'X' in verticalString:
					consecutiveX = 0 + max(len(s) for s in re.findall(r'X+', verticalString))
				if 'Y' in verticalString:
					consecutiveY = 0 + max(len(s) for s in re.findall(r'O+', verticalString))
				value = value - consecutiveX + consecutiveY
		# Horizontal
		for i in range(0, n):
			horizontalString = ""
			for j in range(0, n):
				horizontalString = horizontalString + self.current_state[i][j]
			horizontalString = horizontalString.replace(".", "")
			if len(horizontalString) > 0:
				consecutiveX = 0
				consecutiveY = 0
				if horizontalString in closeToWinX:
					value = value - 15
				if horizontalString in closeToWinO:
					value = value + 15
				for den in denialX:
					if den in horizontalString:
						value = value - 35
				for den in denialO:
					if den in horizontalString:
						value = value + 35
				if len(horizontalString) > 0:
					consecutiveX = 0
					consecutiveY = 0
					if 'X' in horizontalString:
						consecutiveX = 0 + max(len(s) for s in re.findall(r'X+', horizontalString))
					if 'Y' in horizontalString:
						consecutiveY = 0 + max(len(s) for s in re.findall(r'O+', horizontalString))
					value = value - consecutiveX + consecutiveY
		# Diagonal win
		h, w = len(self.current_state), len(self.current_state[0])

		diagList = [[self.current_state[h - 1 - q][p - q]
					 for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
					for p in range(h + w - 1)]
		for i in range(0, len(diagList)):
			diagonalString = ""
			for j in range(0, len(diagList[i])):
				diagonalString = diagonalString + diagList[i][j]
			if len(diagonalString) >= s:
				if diagonalString in closeToWinX:
					value = value - 15
				if diagonalString in closeToWinO:
					value = value + 15
				for den in denialX:
					if den in diagonalString:
						value = value - 35
				for den in denialO:
					if den in diagonalString:
						value = value + 35
				if len(diagonalString) > 0:
					consecutiveX = 0
					consecutiveY = 0
					if 'X' in diagonalString:
						consecutiveX = 0 + max(len(s) for s in re.findall(r'X+', diagonalString))
					if 'Y' in diagonalString:
						consecutiveY = 0 + max(len(s) for s in re.findall(r'O+', diagonalString))
					value = value - consecutiveX + consecutiveY

		antiDiagList = [[self.current_state[p - q][q]
						 for q in range(max(p - h + 1, 0), min(p + 1, w))]
						for p in range(h + w - 1)]
		for i in range(0, len(antiDiagList)):
			diagonalString = ""
			for j in range(0, len(antiDiagList[i])):
				diagonalString = diagonalString + antiDiagList[i][j]
			if len(diagonalString) >= s:
				if diagonalString in closeToWinX:
					value = value - 15
				if diagonalString in closeToWinO:
					value = value + 15
				for den in denialX:
					if den in diagonalString:
						value = value - 35
				for den in denialO:
					if den in diagonalString:
						value = value + 35
				if len(diagonalString) > 0:
					consecutiveX = 0
					consecutiveY = 0
					if 'X' in diagonalString:
						consecutiveX = 0 + max(len(s) for s in re.findall(r'X+', diagonalString))
					if 'Y' in diagonalString:
						consecutiveY = 0 + max(len(s) for s in re.findall(r'O+', diagonalString))
					value = value - consecutiveX + consecutiveY
		return value

	def input_move(self, n):
		while True:
			text1 = 'Enter the x coordinate (as a capital letter from A to {0}...): '.format(chr(ord('A')+n-1))
			text2 = 'Enter the y coordinate (as a number from 0 to {}): '.format(n-1)
			print(F'Player {self.player_turn}, enter your move:')
			px = input(text1)
			py = int(input(text2))
			px = self.convert_input_x(px)
			if self.is_valid(px, py, n):
				return (px,py)
			else:
				print('The move is not valid! You may try again.')

	def switch_player(self):
		if self.player_turn == 'X':
			self.player_turn = 'O'
		elif self.player_turn == 'O':
			self.player_turn = 'X'
		return self.player_turn

	def minimax(self, max=False, n=3, s=3, d=4, iter=0, startTime=0, t=10, e=E1):
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
			return (-9999, x, y)
		elif result == 'O':
			return (9999, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, n):
			for j in range(0, n):
				if self.current_state[i][j] == '.':
					if x == None:
						x = i
					if y == None:
						y = j
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.minimax(max=False, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t, e=e)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.minimax(max=True, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t, e=e)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
					timeElapsed = time.time() - startTime
					if iter > d or timeElapsed >= t - (t * 0.0075):
						if e == self.E1:
							return (self.e1_heuristic(n=n, s=s), x, y)
						else:
							return (self.e2_heuristic(n=n, s=s), x, y)
		if e == self.E1:
			return (self.e1_heuristic(n=n, s=s), x, y)
		else:
			return (self.e2_heuristic(n=n, s=s), x, y)

	def alphabeta(self, alpha=-2, beta=2, max=False, n=3, s=3, d=4, iter=0, startTime=0, t=10, e=E1):
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
			return (-9999, x, y)
		elif result == 'O':
			return (9999, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, n):
			for j in range(0, n):
				if self.current_state[i][j] == '.':
					if x == None:
						x = i
					if y == None:
						y = j
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.alphabeta(alpha, beta, max=False, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t, e=e)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.alphabeta(alpha, beta, max=True, n=n, s=s, d=d, iter=iter+1, startTime=startTime, t=t, e=e)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
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
					timeElapsed = round(time.time() - startTime, 7)
					if iter > d or timeElapsed >= t - (t * 0.0075):
						if e == self.E1:
							return (self.e1_heuristic(n=n, s=s), x, y)
						else:
							return (self.e2_heuristic(n=n, s=s), x, y)
		if e == self.E1:
			return (self.e1_heuristic(n=n, s=s), x, y)
		else:
			return (self.e2_heuristic(n=n, s=s), x, y)

	def place_blocs(self, b=0, n=3):
		if b > 0:
			blocPlacements = []
			yesNo = -1
			choosePlacement = False
			while yesNo != 0 and yesNo != 1:
				yesNo = int(input("Would you like to choose where to place the blocs? Enter 1 for yes, 0 for no: "))
				if yesNo == 0:
					choosePlacement = False
				elif yesNo == 1:
					choosePlacement = True
				elif yesNo != 0 and yesNo != 1:
					print("Your input must be either 0 for no or 1 for yes! Please try again.")
			if choosePlacement:
				for i in range(b):
					while True:
						displayText = "Enter the coordinate for bloc number {}:".format(i+1)
						text1 = 'Enter the x coordinate (as a capital letter from A to {}...): '.format(chr(ord('A') + n - 1))
						text2 = 'Enter the y coordinate (as a number from 0 to {}): '.format(n - 1)
						print(displayText)
						inputX = input(text1)
						py = int(input(text2))
						px = self.convert_input_x(inputX)
						if self.is_valid(px, py, n) and self.current_state[px][py] != '*':
							self.current_state[px][py] = '*'
							blocPlacements.append(tuple([inputX, py]))
							break
						else:
							print('The coordinates are invalid or there is already a bloc there. You may try again.')
			else:
				for i in range(b):
					while True:
						px = random.randint(0, n-1)
						py = random.randint(0, n-1)
						if self.current_state[px][py] == '*':
							continue
						else:
							self.current_state[px][py] = '*'
							inputX = self.convert_x_to_input(px)
							blocPlacements.append(tuple([inputX, py]))
							break
			print("blocs ={}".format(blocPlacements))

	def play(self,algo=True,player_x=None,player_o=None,n=3,s=3,d1=4,d2=4,t=10,p1e=E1,p2e=E2):
		moveNum = 0
		if algo == True:
			algo = self.ALPHABETA
		elif algo == False:
			algo = self.MINIMAX
		if player_x == None:
			player_x = self.HUMAN
		if player_o == None:
			player_o = self.HUMAN
		while True:
			moveNum = moveNum + 1
			self.draw_board(size=n, moveNum=moveNum)
			if self.check_end(n, s):
				return
			start = time.time()
			if algo == self.MINIMAX:
				if self.player_turn == 'X':
					(_, x, y) = self.minimax(max=False, n=n, s=s, d=d1, iter=0, startTime=start, t=t, e=p1e)
				else:
					(_, x, y) = self.minimax(max=True, n=n, s=s, d=d2, iter=0, startTime=start, t=t, e=p2e)
			else: # algo == self.ALPHABETA
				if self.player_turn == 'X':
					(m, x, y) = self.alphabeta(max=False, n=n, s=s, d=d1, iter=0, startTime=start, t=t, e=p1e)
				else:
					(m, x, y) = self.alphabeta(max=True, n=n, s=s, d=d2, iter=0, startTime=start, t=t, e=p2e)
			end = time.time()
			if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
					if self.recommend:
						print(F'Evaluation time: {round(end - start, 7)}s')
						xDisplay = self.convert_x_to_input(x)
						print(F'Recommended move: x = {xDisplay}, y = {y}')
					print(F'Player {self.player_turn} under Human control plays: x = {xDisplay}, y = {y}')
					(x,y) = self.input_move(n)
			if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
					print(F'Evaluation time: {round(end - start, 7)}s')
					xDisplay = self.convert_x_to_input(x)
					print(F'Player {self.player_turn} under AI control plays: x = {xDisplay}, y = {y}')
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
		pin2 = int(input("Should player 2 be human controlled? Enter 1 for yes, 0 for no: "))
		if pin2 == 0:
			player2 = Game.AI
		elif pin2 == 1:
			player2 = Game.HUMAN
		elif pin2 != 0 and pin2 != 1:
			print("Your input must be either 0 for no or 1 for yes! Please try again.")
	reccoBool = True
	if pin1 == 1 or pin2 == 1:
		recco = -1
		while recco != 0 and recco != 1:
			recco = int(input("Would the players like to be recommended moves by the algorithm? Enter 1 for yes, 0 for no: "))
			if recco == 0:
				reccoBool = False
			elif recco == 1:
				reccoBool = True
			elif recco != 0 and recco != 1:
				print("Your input must be either 0 for no or 1 for yes! Please try again.")
	p1e = Game.E1
	p1eChoice = -1
	while p1eChoice != 0 and p1eChoice != 1:
		p1eChoice = int(input("Choose the heuristic function for player 1. Enter 1 for e1 or 0 for e2: "))
		if p1eChoice == 1:
			p1e = Game.E1
		elif p1eChoice == 0:
			p1e = Game.E2
		elif p1eChoice != 0 and p1eChoice != 1:
			print("Your input must be either 0 for e2 or 1 for p1e! Please try again.")
	p2e = Game.E2
	p2eChoice = -1
	while p2eChoice != 0 and p2eChoice != 1:
		p2eChoice = int(input("Choose the heuristic function for player 2. Enter 1 for e1 or 0 for e2: "))
		if p2eChoice == 1:
			p2e = Game.E1
		elif p2eChoice == 0:
			p2e = Game.E2
		elif p2eChoice != 0 and p2eChoice != 1:
			print("Your input must be either 0 for p2e or 1 for p2e! Please try again.")
	return n, b, s, d1, d2, t, a, player1, player2, reccoBool, p1e, p2e

def main():
	n, b, s, d1, d2, t, a, player1, player2, reccoBool, p1e, p2e = receiveInputs()
	if (a):
		algo = Game.MINIMAX
	else:
		algo = Game.ALPHABETA
	g = Game(recommend=reccoBool, n=n)
	g.place_blocs(b=b, n=n)
	g.play(algo=algo,player_x=player1,player_o=player2,n=n,s=s,d1=d1,d2=d2,t=t, p1e=p1e, p2e=p2e)

if __name__ == "__main__":
	main()

