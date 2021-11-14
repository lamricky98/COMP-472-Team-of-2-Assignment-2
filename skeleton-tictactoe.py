# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python
import re
import sys
import time
import random
import itertools
import copy


def print_initial_state(f, score_f, n, b, s, t, p1e, p2e, algo, blocs, d1, d2):
    print('n={} b={} s={} t={}\n'.format(n, b, s, t), file=f, flush=True)
    print('blocs={}\n'.format(blocs), file=f, flush=True)
    print('Player 1: AI d={} a={} {}(regular)'.format(d1, algo == 0, 'e1' if p1e == 4 else 'e2'), file=f, flush=True)
    print('Player 2: AI d={} a={} {}(defensive)'.format(d2, algo == 0, 'e1' if p2e == 4 else 'e2'), file=f, flush=True)
    # Score file:
    print('n={} b={} s={} t={}\n'.format(n, b, s, t), file=score_f, flush=True)
    print('Player 1: AI d={} a={}'.format(d1, algo == 0), file=score_f, flush=True)
    print('Player 2: AI d={} a={}'.format(d2, algo == 0), file=score_f, flush=True)


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    E1 = 4
    E2 = 5
    Stat = {}
    total_move = 0
    total_eval_time = 0
    total_heuri_eval_num = 0
    local_heuri_eval_num = 0
    e1_win = 0
    e2_win = 0

    def __init__(self, recommend=True, n=3, b=0):
        self.initialize_game(n)
        self.recommend = recommend

    def initialize_game(self, n):
        self.current_state = [['.' for i in range(n)] for j in range(n)]
        # Player X or 1 always plays first
        self.player_turn = 'X'

    def draw_board(self, size=3, move_num=0, f=None):
        print()
        print("", file=f, flush=True)
        header = "  "
        top_line = " +"
        for i in range(size):
            header = header + chr(ord('A') + i)
            top_line = top_line + "-"
        header = "{0}  (move #{1})".format(header, move_num)
        print(header)
        print(top_line)

        print(header, file=f, flush=True)
        print(top_line, file=f, flush=True)

        for y in range(0, size):
            print(F'{y}|', end="")
            print(F'{y}|', end="", file=f, flush=True)
            for x in range(0, size):
                print(F'{self.current_state[x][y]}', end="")
                print(F'{self.current_state[x][y]}', end="", file=f, flush=True)
            print()
            print("", file=f, flush=True)
        print()
        print("", file=f, flush=True)

    def convert_input_x(self, px):
        input_x = 0
        if px == "A":
            input_x = 0
        elif px == "B":
            input_x = 1
        elif px == "C":
            input_x = 2
        elif px == "D":
            input_x = 3
        elif px == "E":
            input_x = 4
        elif px == "F":
            input_x = 5
        elif px == "G":
            input_x = 6
        elif px == "H":
            input_x = 7
        elif px == "I":
            input_x = 8
        elif px == "J":
            input_x = 9
        else:
            input_x = -1
        return input_x

    def convert_x_to_input(self, x):
        return chr(ord('A') + x)

    def is_valid(self, px, py, n):
        if px < 0 or px > n - 1 or py < 0 or py > n - 1:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self, n, s):
        win_string_x = 'X' * s
        win_string_o = 'O' * s
        # Vertical win
        transposed_array = [list(i) for i in zip(*self.current_state)]
        for i in range(0, n):
            vertical_string = ""
            for j in range(0, n):
                vertical_string = vertical_string + transposed_array[i][j]
            if win_string_x in vertical_string:
                return 'X'
            elif win_string_o in vertical_string:
                return 'O'
        # Horizontal win
        for i in range(0, n):
            horizontal_string = ""
            for j in range(0, n):
                horizontal_string = horizontal_string + self.current_state[i][j]
            if win_string_x in horizontal_string:
                return 'X'
            elif win_string_o in horizontal_string:
                return 'O'
        # Diagonal win
        h, w = len(self.current_state), len(self.current_state[0])

        diag_list = [[self.current_state[h - 1 - q][p - q]
                      for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
                     for p in range(h + w - 1)]
        for i in range(0, len(diag_list)):
            diagonal_string = ""
            for j in range(0, len(diag_list[i])):
                diagonal_string = diagonal_string + diag_list[i][j]
            if win_string_x in diagonal_string:
                return 'X'
            elif win_string_o in diagonal_string:
                return 'O'

        anti_diag_list = [[self.current_state[p - q][q]
                           for q in range(max(p - h + 1, 0), min(p + 1, w))]
                          for p in range(h + w - 1)]
        for i in range(0, len(anti_diag_list)):
            diagonal_string = ""
            for j in range(0, len(anti_diag_list[i])):
                diagonal_string = diagonal_string + anti_diag_list[i][j]
            if win_string_x in diagonal_string:
                return 'X'
            elif win_string_o in diagonal_string:
                return 'O'
        # Is whole board full?
        for i in range(0, n):
            for j in range(0, n):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == '.':
                    return None
        # It's a tie!
        return '.'

    def check_end(self, n, s, f):
        self.result = self.is_end(n, s)
        # Printing the appropriate message if the game has ended
        if self.result is not None:
            if self.result == 'X':
                self.e1_win += 1
                print('The winner is X!')
                print('The winner is X!', file=f, flush=True)
            elif self.result == 'O':
                self.e2_win += 1
                print('The winner is O!')
                print('The winner is O!', file=f, flush=True)
            elif self.result == '.':
                self.e2_win = 1
                self.e1_win = 1
                print("It's a tie!")
                print("It's a tie!", file=f, flush=True)
        # self.initialize_game()
        return self.result

    def e1_heuristic(self, n=3, s=3, eval_num=0):
        # Simple heuristic optimized for X
        # Lower value is better for X
        # Higher value is better for O
        value = 0
        # Vertical
        transposed_array = [list(i) for i in zip(*self.current_state)]
        for i in range(0, n):
            vertical_string = ""
            for j in range(0, n):
                vertical_string = vertical_string + transposed_array[i][j]
            value = value - vertical_string.count('X') + vertical_string.count('O')
            eval_num += 1
            self.total_heuri_eval_num += 1

        # Horizontal
        for i in range(0, n):
            horizontal_string = ""
            for j in range(0, n):
                horizontal_string = horizontal_string + self.current_state[i][j]
            value = value - horizontal_string.count('X') + horizontal_string.count('O')
            eval_num += 1
            self.total_heuri_eval_num += 1
        # Diagonal win
        h, w = len(self.current_state), len(self.current_state[0])

        diag_list = [[self.current_state[h - 1 - q][p - q]
                      for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
                     for p in range(h + w - 1)]
        for i in range(0, len(diag_list)):
            diagonal_string = ""
            for j in range(0, len(diag_list[i])):
                diagonal_string = diagonal_string + diag_list[i][j]
            if len(diagonal_string) >= s:
                value = value - diagonal_string.count('X') + diagonal_string.count('O')
            self.total_heuri_eval_num += 1
            eval_num += 1

        anti_diag_list = [[self.current_state[p - q][q]
                           for q in range(max(p - h + 1, 0), min(p + 1, w))]
                          for p in range(h + w - 1)]
        for i in range(0, len(anti_diag_list)):
            diagonal_string = ""
            for j in range(0, len(anti_diag_list[i])):
                diagonal_string = diagonal_string + anti_diag_list[i][j]
            if len(diagonal_string) >= s:
                value = value - diagonal_string.count('X') + diagonal_string.count('O')
                eval_num += 1
            self.total_heuri_eval_num += 1
        return value

    def e2_heuristic(self, n=3, s=3):
        # Slightly more complex heuristic, biased on defensive
        # Lower value is better for X
        # Higher value is better for O
        winning_string_x = 'X' * (s - 2) + '..'
        close_to_win_x = list(set(''.join(p) for p in itertools.permutations(winning_string_x)))
        winning_string_x = 'X' * (s - 1) + '.'
        close_to_win_x = close_to_win_x + list(set(''.join(p) for p in itertools.permutations(winning_string_x)))
        winning_string_o = 'O' * (s - 2) + '..'
        close_to_win_o = list(set(''.join(p) for p in itertools.permutations(winning_string_o)))
        winning_string_o = 'O' * (s - 1) + '.'
        close_to_win_o = close_to_win_o + list(set(''.join(p) for p in itertools.permutations(winning_string_o)))
        denial_o_chars = 'X' * (s - 1) + 'O'
        denial_x_chars = 'O' * (s - 1) + 'X'
        denial_o = list(set(''.join(p) for p in itertools.permutations(denial_o_chars)))
        denial_x = list(set(''.join(p) for p in itertools.permutations(denial_x_chars)))
        value = 0
        # Vertical
        transposed_array = [list(i) for i in zip(*self.current_state)]
        for i in range(0, n):
            vertical_string = ""
            for j in range(0, n):
                vertical_string = vertical_string + transposed_array[i][j]
            for near_win in close_to_win_x:
                self.total_heuri_eval_num += 1
                if near_win in vertical_string:
                    value = value - 15
            for near_win in close_to_win_o:
                self.total_heuri_eval_num += 1
                if near_win in vertical_string:
                    value = value + 15
            for den in denial_x:
                self.total_heuri_eval_num += 1
                if den in vertical_string:
                    value = value - 50
            for den in denial_o:
                self.total_heuri_eval_num += 1
                if den in vertical_string:
                    value = value + 50
            if '*' in vertical_string:
                partitioned_string = vertical_string.partition('*')
                before_star = partitioned_string[0]
                after_star = partitioned_string[2]
                consecutive_x = 0
                consecutive_y = 0
                if len(before_star) >= s:
                    if before_star.count('X') > 1:
                        consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', before_star)) * 2)
                    if before_star.count('Y') > 1:
                        consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', before_star)) * 2)
                    value = value - consecutive_x + consecutive_y
                consecutive_x = 0
                consecutive_y = 0
                if len(after_star) >= s:
                    if after_star.count('X') > 1:
                        consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', after_star)) * 2)
                    if after_star.count('Y') > 1:
                        consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', after_star)) * 2)
                    value = value - consecutive_x + consecutive_y
            else:
                value = value - vertical_string.count('X') + vertical_string.count('O')
            self.total_heuri_eval_num += 1
        # Horizontal
        for i in range(0, n):
            horizontal_string = ""
            for j in range(0, n):
                horizontal_string = horizontal_string + self.current_state[i][j]
            horizontal_string = horizontal_string.replace(".", "")
            if len(horizontal_string) > 0:
                consecutive_x = 0
                consecutive_y = 0
                for near_win in close_to_win_x:
                    self.total_heuri_eval_num += 1
                    if near_win in horizontal_string:
                        value = value - 15
                for near_win in close_to_win_o:
                    self.total_heuri_eval_num += 1
                    if near_win in horizontal_string:
                        value = value + 15
                for den in denial_x:
                    self.total_heuri_eval_num += 1
                    if den in horizontal_string:
                        value = value - 50
                for den in denial_o:
                    self.total_heuri_eval_num += 1
                    if den in horizontal_string:
                        value = value + 50
                if '*' in horizontal_string:
                    partitioned_string = horizontal_string.partition('*')
                    before_star = partitioned_string[0]
                    after_star = partitioned_string[2]
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(before_star) >= s:
                        if before_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', before_star)) * 2)
                        if before_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', before_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(after_star) >= s:
                        if after_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', after_star)) * 2)
                        if after_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', after_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                else:
                    value = value - horizontal_string.count('X') + horizontal_string.count('O')
                self.total_heuri_eval_num += 1
        # Diagonal win
        h, w = len(self.current_state), len(self.current_state[0])

        diag_list = [[self.current_state[h - 1 - q][p - q]
                      for q in range(min(p, h - 1), max(0, p - w + 1) - 1, -1)]
                     for p in range(h + w - 1)]
        for i in range(0, len(diag_list)):
            diagonal_string = ""
            for j in range(0, len(diag_list[i])):
                diagonal_string = diagonal_string + diag_list[i][j]
            if len(diagonal_string) >= s:
                for near_win in close_to_win_x:
                    self.total_heuri_eval_num += 1
                    if near_win in diagonal_string:
                        value = value - 15
                for near_win in close_to_win_o:
                    self.total_heuri_eval_num += 1
                    if near_win in diagonal_string:
                        value = value + 15
                for den in denial_x:
                    self.total_heuri_eval_num += 1
                    if den in diagonal_string:
                        value = value - 50
                for den in denial_o:
                    self.total_heuri_eval_num += 1
                    if den in diagonal_string:
                        value = value + 50
                if '*' in diagonal_string:
                    partitioned_string = diagonal_string.partition('*')
                    before_star = partitioned_string[0]
                    after_star = partitioned_string[2]
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(before_star) >= s:
                        if before_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', before_star)) * 2)
                        if before_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', before_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(after_star) >= s:
                        if after_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', after_star)) * 2)
                        if after_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', after_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                else:
                    value = value - diagonal_string.count('X') + diagonal_string.count('O')
                self.total_heuri_eval_num += 1

        anti_diag_list = [[self.current_state[p - q][q]
                           for q in range(max(p - h + 1, 0), min(p + 1, w))]
                          for p in range(h + w - 1)]
        for i in range(0, len(anti_diag_list)):
            diagonal_string = ""
            for j in range(0, len(anti_diag_list[i])):
                diagonal_string = diagonal_string + anti_diag_list[i][j]
            if len(diagonal_string) >= s:
                for near_win in close_to_win_x:
                    self.total_heuri_eval_num += 1
                    if near_win in diagonal_string:
                        value = value - 15
                for near_win in close_to_win_o:
                    self.total_heuri_eval_num += 1
                    if near_win in diagonal_string:
                        value = value + 15
                for den in denial_x:
                    self.total_heuri_eval_num += 1
                    if den in diagonal_string:
                        value = value - 50
                for den in denial_o:
                    self.total_heuri_eval_num += 1
                    if den in diagonal_string:
                        value = value + 50
                if '*' in diagonal_string:
                    partitioned_string = diagonal_string.partition('*')
                    before_star = partitioned_string[0]
                    after_star = partitioned_string[2]
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(before_star) >= s:
                        if before_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', before_star)) * 2)
                        if before_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', before_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                    consecutive_x = 0
                    consecutive_y = 0
                    if len(after_star) >= s:
                        if after_star.count('X') > 1:
                            consecutive_x = 0 + (max(len(s) for s in re.findall(r'X+', after_star)) * 2)
                        if after_star.count('Y') > 1:
                            consecutive_y = 0 + (max(len(s) for s in re.findall(r'O+', after_star)) * 2)
                        value = value - consecutive_x + consecutive_y
                else:
                    value = value - diagonal_string.count('X') + diagonal_string.count('O')
                self.total_heuri_eval_num += 1
        return value

    def input_move(self, n):
        while True:
            text1 = 'Enter the x coordinate (as a capital letter from A to {0}...): '.format(chr(ord('A') + n - 1))
            text2 = 'Enter the y coordinate (as a number from 0 to {}): '.format(n - 1)
            print(F'Player {self.player_turn}, enter your move:')
            px = input(text1)
            py = int(input(text2))
            px = self.convert_input_x(px)
            if self.is_valid(px, py, n):
                return px, py
            else:
                print('The move is not valid! You may try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def minimax(self, max=False, n=3, s=3, d=4, iter=0, start_time=0, t=10, e=E1):
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
            return -9999, x, y
        elif result == 'O':
            return 9999, x, y
        elif result == '.':
            return 0, x, y
        for i in range(0, n):
            for j in range(0, n):
                if self.current_state[i][j] == '.':
                    if x is None:
                        x = i
                    if y is None:
                        y = j
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False, n=n, s=s, d=d, iter=iter + 1,
                                                 start_time=start_time, t=t,
                                                 e=e)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True, n=n, s=s, d=d, iter=iter + 1,
                                                 start_time=start_time, t=t,
                                                 e=e)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    time_elapsed = time.time() - start_time
                    if iter > d or time_elapsed >= t - (t * 0.0075):
                        if e == self.E1:
                            return self.e1_heuristic(n=n, s=s), x, y
                        else:
                            return self.e2_heuristic(n=n, s=s), x, y
        if e == self.E1:
            return self.e1_heuristic(n=n, s=s), x, y
        else:
            return self.e2_heuristic(n=n, s=s), x, y

    def alphabeta(self, alpha=-2, beta=2, max=False, n=3, s=3, d=4, iter=0, start_time=0, t=10, e=E1):
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
            return -9999, x, y
        elif result == 'O':
            return 9999, x, y
        elif result == '.':
            return 0, x, y
        for i in range(0, n):
            for j in range(0, n):
                if self.current_state[i][j] == '.':
                    if x is None:
                        x = i
                    if y is None:
                        y = j
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False, n=n, s=s, d=d, iter=iter + 1,
                                                   start_time=start_time, t=t, e=e)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True, n=n, s=s, d=d, iter=iter + 1,
                                                   start_time=start_time, t=t, e=e)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return value, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y
                        if value < beta:
                            beta = value
                    time_elapsed = round(time.time() - start_time, 7)
                    if iter > d or time_elapsed >= t - (t * 0.0075):
                        if e == self.E1:
                            return self.e1_heuristic(n=n, s=s), x, y
                        else:
                            return self.e2_heuristic(n=n, s=s), x, y
        if e == self.E1:
            return self.e1_heuristic(n=n, s=s), x, y
        else:
            return self.e2_heuristic(n=n, s=s), x, y

    def place_blocs(self, b=0, n=3):
        if b > 0:
            bloc_placements = []
            yes_no = -1
            choose_placement = False
            while yes_no != 0 and yes_no != 1:
                yes_no = int(input("Would you like to choose where to place the blocs? Enter 1 for yes, 0 for no: "))
                if yes_no == 0:
                    choose_placement = False
                elif yes_no == 1:
                    choose_placement = True
                elif yes_no != 0 and yes_no != 1:
                    print("Your input must be either 0 for no or 1 for yes! Please try again.")
            if choose_placement:
                for i in range(b):
                    while True:
                        display_text = "Enter the coordinate for bloc number {}:".format(i + 1)
                        text1 = 'Enter the x coordinate (as a capital letter from A to {}...): '.format(
                            chr(ord('A') + n - 1))
                        text2 = 'Enter the y coordinate (as a number from 0 to {}): '.format(n - 1)
                        print(display_text)
                        input_x = input(text1)
                        py = int(input(text2))
                        px = self.convert_input_x(input_x)
                        if self.is_valid(px, py, n) and self.current_state[px][py] != '*':
                            self.current_state[px][py] = '*'
                            bloc_placements.append(tuple([input_x, py]))
                            break
                        else:
                            print('The coordinates are invalid or there is already a bloc there. You may try again.')
            else:
                for i in range(b):
                    while True:
                        px = random.randint(0, n - 1)
                        py = random.randint(0, n - 1)
                        if self.current_state[px][py] == '*':
                            continue
                        else:
                            self.current_state[px][py] = '*'
                            input_x = self.convert_x_to_input(px)
                            bloc_placements.append(tuple([input_x, py]))
                            break
            self.bloc_snapshot = copy.deepcopy(self.current_state)
            print("blocs ={}".format(bloc_placements))
            return bloc_placements

    def play(self, algo=True, player_x=None, player_o=None, n=3, s=3, d1=4, d2=4, t=10, p1e=E1, p2e=E2, f=None):
        if algo:
            algo = self.ALPHABETA
        elif not algo:
            algo = self.MINIMAX
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN
        self.current_state = copy.deepcopy(self.bloc_snapshot)

        while True:
            self.total_move = self.total_move + 1
            self.draw_board(size=n, move_num=self.total_move, f=f)
            if self.check_end(n, s, f):
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False, n=n, s=s, d=d1, iter=0, start_time=start,
                                             t=t, e=p1e)
                else:
                    (_, x, y) = self.minimax(max=True, n=n, s=s, d=d2, iter=0, start_time=start,
                                             t=t, e=p2e)
            else:  # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False, n=n, s=s, d=d1, iter=0, start_time=start, t=t, e=p1e)
                else:
                    (m, x, y) = self.alphabeta(max=True, n=n, s=s, d=d2, iter=0, start_time=start, t=t, e=p2e)
            end = time.time()
            self.total_eval_time += end - start
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'i:  Evaluation time: {round(end - start, 7)}s')
                    print(F'i:  Evaluation time: {round(end - start, 7)}s', file=f, flush=True)
                    x_display = self.convert_x_to_input(x)
                    print(F'Recommended move: x = {x_display}, y = {y}', file=f, flush=True)
                    print(F'Player {self.player_turn} under Human control plays: x = {x_display}, y = {y}')
                    print(F'Player {self.player_turn} under Human control plays: x = {x_display}, y = {y}', file=f,
                          flush=True)
                (x, y) = self.input_move(n)
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Evaluation time: {round(end - start, 7)}s', file=f, flush=True)
                x_display = self.convert_x_to_input(x)
                print(F'Player {self.player_turn} under AI control plays: x = {x_display}, y = {y}')
                print(F'Player {self.player_turn} under AI control plays: x = {x_display}, y = {y}', file=f, flush=True)
            self.current_state[x][y] = self.player_turn
            self.switch_player()


def receive_inputs():
    n = 0
    while n < 3 or n > 10:
        n = int(input("Enter size n of the board: "))
        if n < 3 or n > 10:
            print("n must be a value between 3 and 10! Please try again.")
    b = -1
    while b < 0 or b > 2 * n:
        b = int(input("Enter the number b of the blocs: "))
        if b < 0 or b > 2 * n:
            print("b must be a value between 0 and " + 2 * n + "! Please try again.")
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
    recco_bool = True
    if pin1 == 1 or pin2 == 1:
        recco = -1
        while recco != 0 and recco != 1:
            recco = int(
                input("Would the players like to be recommended moves by the algorithm? Enter 1 for yes, 0 for no: "))
            if recco == 0:
                recco_bool = False
            elif recco == 1:
                recco_bool = True
            elif recco != 0 and recco != 1:
                print("Your input must be either 0 for no or 1 for yes! Please try again.")
    p1e = Game.E1
    p1e_choice = -1
    while p1e_choice != 0 and p1e_choice != 1:
        p1e_choice = int(input("Choose the heuristic function for player 1. Enter 1 for e1 or 0 for e2: "))
        if p1e_choice == 1:
            p1e = Game.E1
        elif p1e_choice == 0:
            p1e = Game.E2
        elif p1e_choice != 0 and p1e_choice != 1:
            print("Your input must be either 0 for e2 or 1 for p1e! Please try again.")
    p2e = Game.E2
    p2e_choice = -1
    while p2e_choice != 0 and p2e_choice != 1:
        p2e_choice = int(input("Choose the heuristic function for player 2. Enter 1 for e1 or 0 for e2: "))
        if p2e_choice == 1:
            p2e = Game.E1
        elif p2e_choice == 0:
            p2e = Game.E2
        elif p2e_choice != 0 and p2e_choice != 1:
            print("Your input must be either 0 for p2e or 1 for p2e! Please try again.")
    return n, b, s, d1, d2, t, a, player1, player2, recco_bool, p1e, p2e


def out_final_summary(f=None, f_score=None, g=Game()):
    print("6(b)i:   Average evaluation time: {}".format(g.total_eval_time / g.total_move))
    print("6(b)ii   Total heuristic evaluations: {}".format(g.total_heuri_eval_num))
    print("6(b)vi:  Total moves: {}".format(g.total_move))

    print("6(b)i:   Average evaluation time: {}".format(g.total_eval_time / g.total_move), file=f, flush=True)
    print("6(b)ii   Total heuristic evaluations: {}".format(g.total_heuri_eval_num), file=f, flush=True)
    print("6(b)vi:  Total moves: {}".format(g.total_move), file=f, flush=True)

    # Score file:
    print("Total wins for heuristic e1: {} ({}%) (regular)".format(g.e1_win, g.e1_win * 100 / (g.e1_win + g.e2_win)),
          file=f_score, flush=True)
    print("Total wins for heuristic e2: {} ({}%) (regular)".format(g.e2_win, g.e2_win * 100 / (g.e1_win + g.e2_win)),
          file=f_score, flush=True)
    print("i   Average evaluation time: {}".format(g.total_eval_time / g.total_move), file=f_score, flush=True)
    print("ii  Total heuristic evaluations: {}".format(g.total_heuri_eval_num), file=f_score, flush=True)
    print("vi  Average moves per game: {}".format(g.total_move / 10), file=f_score, flush=True)


def main():
    n, b, s, d1, d2, t, a, player1, player2, recco_bool, p1e, p2e = receive_inputs()
    if a:
        algo = Game.ALPHABETA
    else:
        algo = Game.MINIMAX
    g = Game(recommend=recco_bool, n=n)
    blocs = g.place_blocs(b=b, n=n)

    score_board_file_name = 'scoreboard.txt'
    file_name = 'gameTrace-{}{}{}{}.txt'.format(n, b, s, t)
    f = open(file_name, 'w+')
    f_score_board = open(score_board_file_name, 'w+')
    print_initial_state(f, f_score_board, n, b, s, t, p1e, p2e, algo, blocs, d1, d2)

    g.play(algo=algo, player_x=player1, player_o=player2, n=n, s=s, d1=d1, d2=d2, t=t, p1e=p1e, p2e=p2e, f=f)
    # g.play(algo=algo, player_x=player2, player_o=player1, n=n, s=s, d1=d1, d2=d2, t=t, p1e=p2e, p2e=p1e, f=f)

    out_final_summary(f, f_score_board, g)


if __name__ == "__main__":
    main()
