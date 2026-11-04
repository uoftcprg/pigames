from dataclasses import dataclass, field, KW_ONLY
from functools import cache, partial
from math import isclose
from operator import getitem, itemgetter
from typing import ClassVar

from pigames.engines import Engine


@dataclass
class TicTacToeEngine(Engine):
    DIMENSION: ClassVar[int] = 3
    CELL_COUNT: ClassVar[int] = DIMENSION ** 2
    EMPTY: ClassVar[str] = '.'
    PLAYERS: ClassVar[str] = 'XO'
    PATTERNS: ClassVar[tuple[tuple[int, int, int], ...]] = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )
    _: KW_ONLY
    _board: str = field(init=False)

    @classmethod
    def _player(cls, board):
        return cls.PLAYERS[(cls.CELL_COUNT - board.count(cls.EMPTY)) % 2]

    @classmethod
    def _play(cls, board, action):
        return board[:action] + cls._player(board) + board[action + 1:]

    @classmethod
    def _result(cls, board):
        for indices in cls.PATTERNS:
            cells = list(map(partial(getitem, board), indices))

            if cells[0] != cls.EMPTY and len(set(cells)) == 1:
                return 1 if cells[0] == 'X' else 0

        return None if cls.EMPTY in board else 0.5

    @classmethod
    def _actions(cls, board):
        for i in range(cls.CELL_COUNT):
            if board[i] == cls.EMPTY:
                value = cls._solve(cls._play(board, i))

                if cls._player(board) == 'O':
                    value = 1 - value

                yield i, value

    @classmethod
    @cache
    def _solve(cls, board):
        value = cls._result(board)

        if value is None:
            _, values = zip(*list(cls._actions(board)))
            value = max(values)

            if cls._player(board) == 'O':
                value = 1 - value

        return value

    @classmethod
    def openings(cls, count, board=None):
        if board is None:
            yield from cls.openings(count, cls.EMPTY * cls.CELL_COUNT)
        elif count:
            actions, values = zip(*cls._actions(board))
            max_value = max(values)

            for action, value in zip(actions, values):
                if isclose(value, max_value):
                    for opening in cls.openings(
                            count - 1,
                            cls._play(board, action),
                    ):
                        yield str(action), *opening
        else:
            yield ()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def reset(self):
        self._board = self.EMPTY * self.CELL_COUNT

    def observe(self):
        return ''.join(self._board)

    def actions(self):
        if self.result() is not None:
            return []

        actions, values = zip(*self._actions(self._board))
        actions = list(zip(map(str, actions), values))

        actions.sort(key=itemgetter(1), reverse=True)

        return actions

    def play(self, action):
        self._board = self._play(self._board, int(action))

    def result(self):
        value = self._result(self._board)

        return None if value is None else (value, 1 - value)
