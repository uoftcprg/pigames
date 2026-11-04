from collections.abc import Callable
from dataclasses import dataclass, field, KW_ONLY
from hashlib import sha256
from math import inf
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen
from typing import Any, ClassVar

from pigames.engines import Engine


@dataclass
class GoEngine(Engine):
    DIMENSION: ClassVar[int] = 19
    CELL_COUNT: ClassVar[int] = DIMENSION ** 2
    EMPTY: ClassVar[str] = '.'
    BLACK: ClassVar[str] = 'B'
    WHITE: ClassVar[str] = 'W'
    _: KW_ONLY
    hash: Callable[[str], str] = lambda key: sha256(key.encode()).hexdigest()
    _engine: Any = field(init=False)
    _actions: list[str] = field(init=False, default_factory=list)
    _previous_boards: set[str] = field(init=False, default_factory=set)

    @classmethod
    def openings(cls, file, count):
        for line in file:
            raw_dimension, *actions = line.split()
            dimension = int(raw_dimension)

            if dimension != cls.DIMENSION:
                continue

            actions.remove('|')

            if len(actions) == count:
                yield tuple(actions)

    @property
    def _side(self):
        return self.WHITE if len(self._actions) & 1 else self.BLACK

    def disconnect(self):
        self._engine.kill()
        self._engine.communicate()

    def _gtp(self, args):
        command = ' '.join(args) + '\n'

        self._engine.stdin.write(command)
        self._engine.stdin.flush()

        return ''.join(iter(self._engine.stdout.readline, '\n'))

    def reset(self):
        self._gtp(['clear_board'])
        self._actions.clear()
        self._previous_boards.clear()

    def _board(self):
        return self._gtp(['showboard'])

    def observe(self):
        board = self._board()
        pass_status = int(bool(self._actions and self._actions[-1] == 'pass'))
        previous_boards = ':'.join(sorted(self._previous_boards))
        observation = f'{board}:{pass_status}:{previous_boards}'

        return self.hash(observation)

    def play(self, action):
        self._previous_boards.add(self._board())
        self._gtp(['play', self._side, action])
        self._actions.append(action)

    def result(self):
        raw_result = self._gtp(['final_score']).split()[-1]

        if raw_result == '0':
            result = 0, 0
        else:
            margin = float(raw_result[2:])

            if raw_result.startswith(self.BLACK + '+'):
                result = margin, -margin
            elif raw_result.startswith(self.WHITE + '+'):
                result = -margin, margin
            else:
                raise ValueError('invalid final score')

        return result


@dataclass
class KataGoEngine(GoEngine):
    engine_path: Path
    model_path: Path
    config_path: Path
    min_moves: int | None = None
    max_moves: int | None = None
    max_visits: int | None = None
    max_time: float | None = None

    def connect(self):
        args = [
            str(self.engine_path),
            'gtp',
            '-model',
            str(self.model_path),
            '-config',
            str(self.config_path),
            '-override-config',
            'allowResignation=false',
        ]

        if self.max_visits is not None:
            args.extend(['-override-config', f'maxVisits={self.max_visits}'])

        if self.max_time is not None:
            args.extend(['-override-config', f'maxTime={self.max_time}'])

        self._engine = Popen(
            args,
            stdin=PIPE,
            stdout=PIPE,
            stderr=DEVNULL,
            text=True,
        )

    def _board(self):
        board = super()._board()
        chars = []

        for line in board.splitlines():
            line = line.lstrip()

            if line and line[0].isdigit():
                for char in line:
                    if char in '.OX':
                        chars.append(char)

        assert len(chars) == self.CELL_COUNT

        return ''.join(chars)

    def actions(self):
        if self._actions[-2:] == ['pass', 'pass']:
            return []

        args = ['kata-search_analyze', self._side]

        if self.min_moves is not None:
            args.extend(['minmoves', str(self.min_moves)])

        if self.min_moves is not None:
            args.extend(['maxmoves', str(self.max_moves)])

        output = self._gtp(args)
        action = output.split('play ')[-1].strip()
        infos = []

        for raw_info in output.split('info ')[1:]:
            tokens = raw_info.split()

            infos.append(dict(zip(tokens[::2], tokens[1::2])))

        max_value = -inf
        actions = []

        for info in infos:
            a = info['move']
            v = (
                float(info['weight'])
                * int(info['edgeVisits'])
                / max(int(info['visits']), 1)
            )
            max_value = max(max_value, v)
            v2 = float(info['utilityLcb'])

            actions.append((a, v, v2))

        actions2 = []
        action2 = action, inf

        for a, v, v2 in actions:
            if a == action:
                action2 = a, v2
            elif v >= 0.15 * max_value:
                actions2.append((a, v2))

        actions2.insert(0, action2)

        return actions2


@dataclass
class GNUGoEngine(GoEngine):
    engine_path: Path
    komi: float | None = None

    def connect(self):
        args = [str(self.engine_path), '--mode', 'gtp']

        if self.komi is not None:
            args.extend(['--komi', str(self.komi)])

        self._engine = Popen(
            args,
            stdin=PIPE,
            stdout=PIPE,
            stderr=DEVNULL,
            text=True,
        )

    def _board(self):
        board = super()._board()
        chars = []

        for line in board.splitlines():
            line = line.lstrip()

            if line and line[0].isdigit():
                for char in line[2:]:
                    if char in '.OX':
                        chars.append(char)
                    elif char == '+':
                        chars.append(self.EMPTY)
                    elif char.isdigit():
                        break

        assert len(chars) == self.CELL_COUNT

        return ''.join(chars)

    def actions(self):
        if self._actions[-2:] == ['pass', 'pass']:
            return []

        side = 'black' if self._side == self.BLACK else 'white'
        output = self._gtp([f'top_moves_{side}'])
        tokens = output.split()[1:]
        actions = list(zip(tokens[::2], map(float, tokens[1::2])))

        assert all(v1 >= v2 for (_, v1), (_, v2) in zip(actions, actions[1:]))

        return actions
