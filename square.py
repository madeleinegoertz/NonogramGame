from enum import Enum


class State(Enum):
    filled = "O",
    blank = ".",
    unknown = " "

class Square(object):

    def __init__(self, state: State = State.unknown):
        self._state = state

    def clone(self):
        return Square(self._state)

    def is_unknown(self) -> bool:
        return self._state == State.unknown

    def is_filled(self) -> bool:
        return self._state == State.filled

    def is_blank(self) -> bool:
        return self._state == State.blank

    def get_state(self) -> State:
        return self._state

    def set_unknown(self):
        self._state = State.unknown

    def set_filled(self):
        self._state = State.filled

    def set_blank(self):
        self._state = State.blank

    def __str__(self) -> str:
        return self._state.value