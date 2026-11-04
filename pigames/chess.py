from collections.abc import Callable
from collections import Counter
from dataclasses import dataclass, field, KW_ONLY
from hashlib import sha256
from itertools import starmap
from pathlib import Path
from typing import Any, ClassVar

from chess.engine import Limit, SimpleEngine
from chess import Board, Move
from chess.pgn import read_game

from pigames.engines import Engine


@dataclass
class ChessEngine(Engine):
    MATE_SCORE: ClassVar[int] = 100000
    engine_path: Path
    multi_pv: int = 1
    limit: Limit = field(default_factory=Limit)
    _: KW_ONLY
    hash: Callable[[str], str] = lambda key: sha256(key.encode()).hexdigest()
    _engine: Any = field(init=False)
    _board: Board = field(init=False, default_factory=Board)
    _game: object = field(init=False)

    @classmethod
    def openings(cls, file):
        while True:
            game = read_game(file)

            if game is None:
                break

            yield tuple(map(str, game.mainline_moves()))

    def connect(self):
        self._engine = SimpleEngine.popen_uci(self.engine_path)

    def disconnect(self):
        self._engine.quit()

    def reset(self):
        self._board = Board()
        self._game = object()

    def observe(self):
        position = self._board.epd()
        history = Counter()
        board = self._board.copy()

        while board.move_stack:
            move = board.pop()

            if board.is_irreversible(move):
                break

            history[board.epd()] += 1

        history = ':'.join(starmap('{}:{}'.format, sorted(history.items())))
        observation = f'{position}:{board.halfmove_clock}:{history}'

        return self.hash(observation)

    def actions(self):
        if self._board.is_game_over():
            return []

        infos = self._engine.analyse(
            self._board,
            self.limit,
            multipv=self.multi_pv,
            game=self._game,
        )
        actions = []

        for info in infos:
            action = str(info['pv'][0])
            value = info['score'].relative.score(mate_score=self.MATE_SCORE)

            actions.append((action, value))

        return actions

    def play(self, action):
        move = Move.from_uci(action)

        if not self._board.is_legal(move):
            raise ValueError('illegal move')

        self._board.push(move)

    def result(self):
        tokens = self._board.result().replace('1/2', '0.5').split('-')

        return tuple(map(float, tokens))
