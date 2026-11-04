from dataclasses import dataclass, field, KW_ONLY
from itertools import chain
from math import inf
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Any, ClassVar

from pigames.engines import Engine


@dataclass
class GomokuEngine(Engine):
    DIMENSION: ClassVar[int] = 15
    CELL_COUNT: ClassVar[int] = DIMENSION ** 2
    EMPTY: ClassVar[str] = '.'
    BLACK: ClassVar[str] = 'B'
    WHITE: ClassVar[str] = 'W'
    MATE_SCORE: ClassVar[int] = 100000
    _: KW_ONLY
    _engine: Any = field(init=False)
    _board: list[list[str]] = field(init=False)
    _actions: list[str] = field(init=False, default_factory=list)

    @classmethod
    def openings(cls, file):

        def normalize(action):
            r, c = map(int, action.split(','))

            return f'{r % cls.DIMENSION},{c % cls.DIMENSION}'

        for line in file:
            yield tuple(map(normalize, line.split(', ')))

    @property
    def _side(self):
        return self.WHITE if len(self._actions) & 1 else self.BLACK

    def disconnect(self):
        self._engine.kill()
        self._engine.communicate()

    def _piskvork(self, args):
        self._engine.stdin.write('\n'.join(args) + '\n')
        self._engine.stdin.flush()
        lines = []

        while not (lines and lines[-1][0].isdigit()):
            line = self._engine.stdout.readline()

            lines.append(line)

        return ''.join(lines)

    def reset(self):
        self._engine.stdin.write('RESTART\n')

        self._board = [
            [self.EMPTY] * self.DIMENSION for _ in range(self.DIMENSION)
        ]

        self._actions.clear()

    def observe(self):
        return ''.join(chain.from_iterable(self._board))

    def play(self, action):
        r, c = map(int, action.split(','))

        assert self._board[r][c] == self.EMPTY

        self._board[r][c] = self._side

        self._actions.append(action)

    def result(self):

        def run(r, c, dr, dc, side, count):
            if count == 0:
                status = True
            elif 0 <= r < self.DIMENSION and 0 <= c < self.DIMENSION:
                status = (
                    self._board[r][c] == side
                    and run(r + dr, c + dc, dr, dc, side, count - 1)
                )
            else:
                status = False

            return status

        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
                    if (
                            self._board[r][c] != self.EMPTY
                            and run(r, c, dr, dc, self._board[r][c], 5)
                    ):
                        return (1, 0) if self._board[r][c] == 'B' else (0, 1)

        return (0.5, 0.5) if len(self._actions) == self.CELL_COUNT else None


@dataclass
class RapfiEngine(GomokuEngine):
    engine_path: Path
    count: int = 1
    max_depth: int | None = None
    timeout_turn: int | None = None

    def connect(self):
        self._engine = Popen(
            [str(self.engine_path)],
            stdin=PIPE,
            stdout=PIPE,
            text=True,
        )

        self._engine.stdin.write(f'START {self.DIMENSION}\n')
        self._engine.stdin.write('INFO SHOW_DETAIL 2\n')

        if self.max_depth is not None:
            self._engine.stdin.write(f'INFO MAX_DEPTH {self.max_depth}\n')

        if self.timeout_turn is not None:
            self._engine.stdin.write(
                f'INFO TIMEOUT_TURN {self.timeout_turn}\n',
            )

        self._engine.stdin.flush()

    def actions(self):
        if self.result() is not None:
            return []

        board = []

        for i, a in enumerate(self._actions):
            side = 1 if i & 1 == len(self._actions) & 1 else 2

            board.append(f'{a},{side}')

        args = ['YXBOARD', '\n'.join(board), 'DONE', f'YXNBEST {self.count}']
        output = self._piskvork(args)
        action = output.splitlines()[-1]
        infos = {}

        for chunk in output.split('INFO PV DONE'):
            info = {}

            for line in chunk.splitlines():
                if line.startswith('INFO '):
                    info.setdefault(*line.split()[1:3])

            if not info:
                continue

            infos[info['PV']] = info

        assert list(map(int, infos.keys())) == list(range(len(infos)))

        actions = []
        action2 = action, inf

        for info in infos.values():
            a = info['BESTLINE']
            score = info['EVAL']

            if score.startswith('-M'):
                v = -(self.MATE_SCORE - int(score[2:]))
            elif score.startswith('+M'):
                v = self.MATE_SCORE - int(score[2:])
            else:
                v = int(score)

            if a == action:
                action2 = a, v
            else:
                actions.append((a, v))

        actions.insert(0, action2)

        return actions
