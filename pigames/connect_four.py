from dataclasses import dataclass, field, KW_ONLY
from functools import partial
from math import isclose
from operator import getitem, itemgetter
from typing import ClassVar

from connect_four_ai import Solver, Position
import numpy as np

from pigames.engines import Engine


@dataclass
class ConnectFourEngine(Engine):
    SOLVER: ClassVar[Solver] = Solver()
    COLUMN_COUNT: ClassVar[int] = 7
    _: KW_ONLY
    _position: Position = field(init=False)

    @classmethod
    def _actions(cls, position):
        scores = cls.SOLVER.get_all_move_scores(position)
        actions = [i for i, score in enumerate(scores) if score is not None]
        scores = list(map(partial(getitem, scores), actions))
        values = (np.array(scores) + 0.5).clip(0, 1).tolist()

        return actions, values

    @classmethod
    def openings(cls, count, moves=''):
        if count:
            try:
                position = Position.from_moves(moves)
            except ValueError:
                pass
            else:
                actions, values = cls._actions(position)
                max_value = max(values)

                for action, value in zip(actions, values):
                    if isclose(value, max_value):
                        for opening in cls.openings(
                                count - 1,
                                moves + str(action + 1),
                        ):
                            yield str(action), *opening
        else:
            yield ()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def reset(self):
        self._position = Position()

    def observe(self):
        return format(self._position.position + self._position.mask, 'x')

    def actions(self):
        actions, values = self._actions(self._position)
        actions = list(zip(map(str, actions), values))

        actions.sort(key=itemgetter(1), reverse=True)

        return actions

    def play(self, action):
        self._position.play(int(action))

    def result(self):
        if self._position.is_won_position():
            return (1, 0) if self._position.get_moves() & 1 else (0, 1)

        for i in range(self.COLUMN_COUNT):
            if self._position.is_playable(i):
                return None

        return 0.5, 0.5
