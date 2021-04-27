from typing import List

# An action is a line (row(s) or column(s)) to be updated. Used by non-naive solvers. 
# is_row: if True, the row(s) to update. If False, the column(s) to update
# indices: the indices of the rows or columns to update. 
# Example: 
# action = Action(True, [0, 2, 3])
# this creates an action that says the next ROWS to be updated are rows 0, 2, and 3. 
class Action(object):

    def __init__(self, is_row: bool, indices = []):
        self._is_row = is_row
        self._indices = indices

    def is_row(self) -> bool:
        return self._is_row

    def get_num_indices(self) -> int:
        return len(self._indices)

    def add_index(self, index: int):
        self._indices.append(index)

    def get_index(self, i: int) -> int:
        return self._indices[i]

    def to_string(self) -> str:
        out = ("ROW:" if self._is_row else "COL:")
        for i in range(len(self._indices)):
            out += " " + str(self._indices[i])
        return out