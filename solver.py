import collections
from typing import List

from action import Action
from puzzle import Puzzle
import datetime

from square import Square


class Solver(object):

    def __init__(self, puzzle: Puzzle):
        self._puzzle = puzzle
        self._actions = []
        # still don't quite understand what the point of this is. 
        # self._row_priority = [puzzle.gr][2]
        # self._col_priority = [puzzle.cols][2]

    # Solve by checking rows and cols in alternating priority order
    # if update_solve: will update priority order after each iteration
    # if queue_solve: will add newest updated squares to top of queue
    def priority_solve(self, update_solve: bool = False, queue_solve: bool = False):
        start_time_us = datetime.datetime.now().microsecond
        if not queue_solve:
            self._prioritize()
        i = 1
        self._init_actions(update_solve)
        while not self._puzzle.is_solved():
            current_action = self._actions.pop(0)
            for i in range(current_action.get_num_indices()):
                self._update_line(current_action.get_index(i), current_action.is_row(), queue_solve)
                self._puzzle.console_print("i = " + str(i))
                i += 1
                if update_solve:
                    self._prioritize()
            if len(self._actions) == 0:
                self._init_actions(update_solve)
        end_time_us = datetime.datetime.now().microsecond
        self._puzzle.print("i = " + str(i))
        self._puzzle.file_print(self._puzzle.__str__())
        self._puzzle.print("Time = %.4f seconds" % ((end_time_us - start_time_us) / 1e12))

    # Naive solving method that checks each row then column until puzzle is solved.
    def slow_solve(self):
        i = 1
        while not self._puzzle.is_solved():
            # for debugging
            self._puzzle.console_print(self._puzzle.__str__())
            r = 0
            while not self._puzzle.is_solved() and r < self._puzzle.rows:
                # self._puzzle.print("r = " + str(r))
                self._update_line(r, True, False)
                i += 1
                r += 1
            c = 0
            while not self._puzzle.is_solved() and c < self._puzzle.cols:
                # self._puzzle.print("c = " + str(c))
                self._update_line(c, False, False)
                i += 1
                c += 1
        self._puzzle.print("i = " + str(i))
        self._puzzle.print(self._puzzle.__str__())

    # Initialize action queue with alternating rows and cols in descending order
    def _init_actions(self, use_priority: bool = False):
        for i in range(max(self._puzzle.rows, self._puzzle.cols)):
            if self._puzzle.is_valid_row(i):
                self._actions.append(Action(True, [self._row_priority[-2][0]] if use_priority else i))
            if self._puzzle.is_valid_col(i):
                self._actions.append(Action(False, [self._col_priority[-2][0]] if use_priority else i))

    def _prioritize(self):
        self._prioritize_line(True)
        self._prioritize_line(False)

    # Sort the line by most inital overlap. Used for priority solver
    def _prioritize_line(self, is_row: bool):
        line_priority = self._row_priority if is_row else self._col_priority
        for i in range(len(line_priority)):
            line_priority[i][0] = i
            line_priority[i][1] = self._max_overlap(i, is_row)
        sorted(line_priority, key=lambda x: x[1], reverse=True)

    # Returns the maximum initial overlap of the largest chunk in a line if it begins blank.
    # Used to prioritize lines for the priority solver.
    def _max_overlap(self, line_num: int, is_row: bool) -> int:
        return self._puzzle.max_clue_val_in_line(line_num, is_row) \
            - self._puzzle.get_num_unknown_squares_in_line(line_num, is_row) \
            + self._puzzle.sum_clues_in_line(line_num, is_row) \
            + len(self._puzzle.get_clues(line_num, is_row)) \
            - 1

    def _update_line(self, line_num: int, is_row: bool, update_actions: bool):
        if not self._puzzle.is_line_correct(line_num, is_row):
            unknown_squares = []  # List of indices of unknown squares in line
            for i in range(self._puzzle.cols if is_row else self._puzzle.rows):
                if self._puzzle.is_unknown(line_num if is_row else i, i if is_row else line_num):
                    unknown_squares.append(i)
            k = self._puzzle.sum_clues_in_line(line_num, is_row) \
                - self._puzzle.num_filled_squares_in_line(line_num, is_row)  # number of squares to fill
            filled_square_guess = self._combin(k, unknown_squares)  # sets of all indices that could be filled
            line_guesses = []  # all possible lines as lists of Squares. All possible, not all valid
            # Populate all possible lines as Square lists
            for i in range(len(filled_square_guess)):  # iterate through every line combination
                new_guess = self._puzzle.get_line(line_num, is_row)
                # Add in new info from guesses
                for j in range(len(filled_square_guess[i])):  # iterate through each element of the guess
                    new_guess[filled_square_guess[i][j]].set_filled()
                # Turn any remaining unknown squares blank
                for j in range(len(new_guess)):
                    if new_guess[j].is_unknown():
                        new_guess[j].set_blank()
                if collections.Counter(self._puzzle.get_clues(line_num, is_row)) \
                        == collections.Counter(self._puzzle.generate_clues_for_line(new_guess)):
                    # if valid guess, add to list
                    line_guesses.append(new_guess)
            # If square is same across all possible valid lines, update grid
            if len(line_guesses) > 0:
                new_action = Action(is_row)
                for i in range(len(line_guesses[0])):
                    is_square_same = self._square_same_across_guesses(i, line_guesses)
                    if is_square_same:
                        is_filled = line_guesses[0][i].is_filled()
                        first = line_num if is_row else i
                        second = i if is_row else line_num
                        if is_filled:
                            self._puzzle.set_filled(first, second)
                        else:
                            self._puzzle.set_blank(first, second)
                        # try:
                        #     unknown_squares.index(i)
                        #     new_action.add_index(i)
                        # except ValueError:
                        #     pass
                if new_action.get_num_indices() > 0 and update_actions:
                    self._actions.insert(0, new_action)

    # Returns list of sets of k elements from data, given that data is sorted ascending
    def _combin(self, k: int, data: List[int]) -> List[List[int]]:
        # list of lists, where each sublist is a valid combination
        combinations = []
        # one individual valid combination
        combin = []
        # Initialize with first lexicographic combination
        for i in range(k):
            combin.append(data[i])
        # last lexicographic combo sum
        sum_last = self._sum_last_combin(k, data)
        # loop while the current sum is less than the last sum
        while sum(combin) < sum_last:
            combinations.append(combin.copy())
            # Generate next combination in lexicographic order
            t = k - 1
            while not t == 0 and combin[t] == data[-k + t]:
                t -= 1
            combin[t] = data[data.index(combin[t]) + 1]
            for i in range(t + 1, k):
                combin[i] = data[data.index(combin[i - 1]) + 1]
        combinations.append(combin.copy())
        return combinations

    # Returns the sum of the elements in the last (in lexicographic order) combination
    # of length k from set data. For use with _combin()
    @staticmethod
    def _sum_last_combin(k: int, data: List[int]) -> int:
        sum_last_combin = 0
        for i in range(k):
            sum_last_combin += data[-1 - i]
        return sum_last_combin

    # Returns True if the square has the same state in a list of a list of squares.
    # Used for line updating algorithm
    @staticmethod
    def _square_same_across_guesses(c: int, line_guesses: List[List[Square]]) -> bool:
        squares_same = True
        i = 1
        while squares_same and i < len(line_guesses):
            squares_same = line_guesses[i][c].get_state() == line_guesses[i - 1][c].get_state()
            i += 1
        return squares_same

    def __str__(self) -> str:
        return self._puzzle.__str__()