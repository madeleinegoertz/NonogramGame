from typing import List


class Action(object):

    def __init__(self, is_row: bool, indices: list = List[int]):
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
