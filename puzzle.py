import collections
import math
from typing import *

from square import Square

SQUARES_PER_SECTION = 5
VERTICAL_DIVIDER = "|"
HORIZONTAL_DIVIDER = "-"


class Puzzle(object):

    def __init__(self, name: str, row_clues_path: str, col_clues_path: str):
        self._row_clues = self._get_clues_from_file(row_clues_path)
        self._col_clues = self._get_clues_from_file(col_clues_path)
        self.rows = len(self._row_clues)
        self.cols = len(self._col_clues)
        self._grid = [[Square() for r in range(self.cols)] for r in range(self.rows)]
        self._outF = open("out\\" + str(name) + ".txt", "a")

    # Returns a list of lists, where clues[] holds one line of clues, 
    # and clues[][] holds the individual clue
    def _get_clues_from_file(self, clues_path: str):
        clues = []
        lines = open(clues_path, 'r').readlines()
        for line in lines:
            num_strs = line.split()
            num_ints = [int(i) for i in num_strs]
            clues.append(num_ints)
        return clues
            
    # True if the configuration of the line generates the correct clues. Note that while
    # one individual line may return that it's correct, it may not be "correct" in the
    # entire context of the puzzle.
    def is_line_correct(self, line_num: int, is_row: bool) -> bool:
        clues = self._row_clues if is_row else self._col_clues
        line = self.get_line(line_num, is_row)
        return self._are_all_squares_known(line_num, is_row) \
            and collections.Counter(clues[line_num]) == collections.Counter(self.generate_clues_for_line(line))

    # True if all square in the line are either filled or blank
    def _are_all_squares_known(self, line_num: int, is_row: bool) -> bool:
        line = self.get_line(line_num, is_row)
        all_known = True
        i = 0
        while all_known and i < len(line):
            all_known = not line[i].is_unknown()
            i += 1
        return all_known

    # True if entire grid is filled out correctly, aka puzzle is complete.
    def is_solved(self) -> bool:
        is_correct = True
        r = 0
        while is_correct and r < self.rows:
            is_correct = self.is_line_correct(r, True)
            r += 1
        c = 0
        while is_correct and c < self.cols:
            is_correct = self.is_line_correct(c, False)
            c += 1
        return is_correct

    # Returns a copy of the requested line in the grid, not a reference to it.
    def get_line(self, line_num: int, is_row: bool) -> List[Square]:
        line = [Square() for i in range(self.cols if is_row else self.rows)]
        for i in range(len(line)):
            line[i] = self._grid[line_num if is_row else i][i if is_row else line_num].clone()
        return line

    # Used for manual game play mode.
    def manual_fill(self, r: int, c: int) -> bool:
        is_valid = self._is_valid_square(r, c)
        if is_valid:
            # Switch between filled and unknown
            self._grid[r][c].set_unknown() if self._grid[r][c].is_filled() else self._grid[r][c].set_filled()
        return is_valid

    # Used for manual game play mode.
    def manual_blank(self, r: int, c: int) -> bool:
        is_valid = self._is_valid_square(r, c)
        if is_valid:
            # Switch between filled and unknown
            self._grid[r][c].set_unknown() if self._grid[r][c].is_blank() else self._grid[r][c].set_blank()
        return is_valid

    def _is_valid_square(self, r: int, c: int) -> bool:
        return self.is_valid_row(r) and self.is_valid_col(c)

    def is_valid_row(self, r: int) -> bool:
        return 0 <= r < self.rows

    def is_valid_col(self, c: int) -> object:
        return 0 <= c < self.cols

    def __str__(self) -> str:
        out = ""
        max_num_row_clues = self._max_num_clues(self._row_clues)
        max_digits_in_row_clues = self._max_digits(self._row_clues) + 1
        print(max_digits_in_row_clues)
        row_clue_space = max_num_row_clues * max_digits_in_row_clues
        # Add all of the column clue labels
        max_num_col_clues = self._max_num_clues(self._col_clues)
        col_clue_space = self._max_digits(self._col_clues) + 1
        ccs = "%" + str(col_clue_space) + "s"
        grid_cols_spaced = (self.rows // SQUARES_PER_SECTION + self.rows + 1) * col_clue_space
        for r in range(max_num_col_clues):  # iterate through the rows of col clues
            out += " " * row_clue_space  # blank space to accommodate row clues
            for c in range(self.cols):  # iterate through each col to get the clue
                clue_val = self._clue_val(c, r, max_num_col_clues, self._col_clues)
                if c % SQUARES_PER_SECTION == 0:
                    out += ccs % VERTICAL_DIVIDER
                out += ccs % (" " if clue_val == 0 else str(clue_val))  # lower justify
            out += ccs % VERTICAL_DIVIDER + "\n"
        # Now onto the row clues and the grid
        hor_div_line = HORIZONTAL_DIVIDER * (row_clue_space + grid_cols_spaced + 1) + "\n"
        for r in range(self.rows):  # iterate through the rows in the puzzle
            if r % SQUARES_PER_SECTION == 0:  # Add horizontal divider if we're at the end of a section
                out += hor_div_line
            # Add the row clues
            for i in range(max_num_row_clues):  # iterate through each row clue
                clue_val = self._clue_val(r, i, max_num_row_clues, self._row_clues)
                rcs = "%" + str(max_digits_in_row_clues) + "s"
                out += rcs % (" " if clue_val == 0 else clue_val)  # lower justify
            # Add values from grid
            for c in range(self.cols):
                if c % SQUARES_PER_SECTION == 0:  # Add vertical dividing line if at end of section
                    out += ccs % VERTICAL_DIVIDER
                out += ccs % self._grid[r][c].__str__()
            # Add end vertical line
            out += ccs % VERTICAL_DIVIDER + "\n"
        # Add bottom horizontal line
        out += hor_div_line
        return out

    # Return the largest value clue in a given line. Eg: If clue is [1 3 2], will return 3
    def max_clue_val_in_line(self, line_num: int, is_row: bool) -> int:
        clues = self._row_clues[line_num] if is_row else self._col_clues[line_num]
        max_val = int("-inf")
        for i in range(len(clues)):
            if clues[i] > max_val:
                max_val = clues[i]
        return max_val

    # Returns copy of clues for line, not a reference to it.
    def get_clues(self, line_num: int, is_row: bool) -> List[int]:
        return self._row_clues[line_num].copy() if is_row else self._col_clues[line_num].copy()

    # Used for determining the max initial overlap in a line, which is used for the priority solver
    def get_num_unknown_squares_in_line(self, line_num: int, is_row: bool) -> int:
        num_unknown_squares = 0
        line = self.get_line(line_num, is_row)
        for i in range(len(line)):
            if line[i].is_unknown():
                num_unknown_squares += 1
        return num_unknown_squares

    # Returns sum of clue values in line. Used for determining max overlap in line for priority solver
    def sum_clues_in_line(self, line_num: int, is_row: bool) -> int:
        clues = self.get_clues(line_num, is_row)
        sum_clues = 0
        for i in range(len(clues)):
            sum_clues += clues[i]
        return sum_clues

    # Returns number of filled squares in line. Used for priority solver.
    def num_filled_squares_in_line(self, line_num: int, is_row: bool) -> int:
        num_filled_squares = 0
        for i in range(self.cols if is_row else self.rows):
            if self.is_filled(line_num if is_row else i, i if is_row else line_num):
                num_filled_squares += 1
        return num_filled_squares

    # Used in __str__() to ensure that the clues are all aligned to the bottom.
    @staticmethod
    def _clue_val(num_clue: int, num_chunk: int, max_num_clues: int, clues) -> int:  # type = clues: List[int][int]
        val = 0
        offset = max_num_clues - len(clues[num_clue])
        if num_chunk >= offset:
            val = clues[num_clue][num_chunk - offset]
        return val

    # Returns the greatest number of clues in either the row clues or col clues, depending
    # on which is passed. Used for __str__() formatting.
    @staticmethod
    def _max_num_clues(clues) -> int:  # type = clues: List[int][int]
        max_num_clues = 0
        for i in range(len(clues)):
            num_clues = len(clues[i])
            if num_clues > max_num_clues:
                max_num_clues = num_clues
        return max_num_clues

    # Returns the max number of digits in either any row clue or any col clue.
    # Used for __str__() formatting
    @staticmethod
    def _max_digits(clues) -> int:  # type = clues: Line[int][int]
        max_digits = 0
        for i in range(len(clues)):
            for j in range(len(clues[i])):
                num_digits = int(math.log10(clues[i][j]))+1
                if num_digits > max_digits:
                    max_digits = num_digits
        return max_digits

    # Given a list of squares (a line), generate the clues for it. Used for
    # determining if possible line configuration would be correct.
    # Ex:
    # line = O O O . . O O O O O
    # return: clues = [3, 5]
    @staticmethod
    def generate_clues_for_line(line: [Square]) -> List[int]:
        clues = []
        is_chunk = False
        len_chunk = 0
        square = None
        for i in range(len(line)):
            square = line[i]
            if is_chunk:  # previous square is filled
                if not square.is_filled():  # O _
                    clues.append(len_chunk)
                    is_chunk = False
                    len_chunk = 0
                else:  # O O
                    len_chunk += 1
            elif square.is_filled():  # _ O
                is_chunk = True
                len_chunk += 1
        # fence posting for last square
        if is_chunk and square.is_filled():
            clues.append(len_chunk)
        return clues

    def is_unknown(self, r: int, c: int) -> bool:
        return self._is_valid_square(r, c) and self._grid[r][c].is_unknown()

    def is_filled(self, r: int, c: int) -> bool:
        return self._is_valid_square(r, c) and self._grid[r][c].is_filled()

    def is_blank(self, r: int, c: int) -> bool:
        return self._is_valid_square(r, c) and self._grid[r][c].is_blank()

    def set_filled(self, r: int, c: int):
        if self._is_valid_square(r, c):
            self._grid[r][c].set_filled()

    def set_blank(self, r: int, c: int):
        if self._is_valid_square(r, c):
            self._grid[r][c].set_blank()

    @staticmethod
    def console_print(text: str):
        print(text)

    def file_print(self, text: str):
        self._outF.write(text)

    def print(self, text: str):
        self.console_print(text)
        self.file_print(text)