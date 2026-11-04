from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from fractions import Fraction
from functools import partial
from hashlib import sha256
from itertools import starmap
from math import sqrt
from operator import itemgetter

from pigames.engines import WrapperEngine

DEFAULT_GAMMA = Fraction(1, 4)
DEFAULT_HASH = lambda key: (  # noqa: E731
    int.from_bytes(sha256(key.encode()).digest())
)


class Color(IntEnum):
    RED = 0
    GREEN = 1


def color(observation, action, gamma=DEFAULT_GAMMA, hash=DEFAULT_HASH):
    h = hash(observation + action)

    return Color(h % gamma.denominator < gamma.numerator)


def _z_score(n_g, n, gamma=DEFAULT_GAMMA):
    return (n_g - gamma * n) / sqrt(n * gamma * (1 - gamma))


def z_scores(matches, gamma=DEFAULT_GAMMA, hash=DEFAULT_HASH):
    matches = list(matches)
    m = len(matches[0].result) if matches else 0
    n_g = [0] * m
    n = [0] * m

    for match in matches:
        for i, observation, action in zip(
                match.indices,
                match.observations,
                match.actions,
        ):
            n_g[i] += color(observation, action, gamma, hash)
            n[i] += 1

        yield tuple(starmap(partial(_z_score, gamma=gamma), zip(n_g, n)))


@dataclass
class WatermarkedEngine(WrapperEngine):
    delta: float
    gamma: Fraction = DEFAULT_GAMMA
    hash: Callable[[str], int] = DEFAULT_HASH

    def actions(self):
        observation = self.observe()
        actions = []

        for action, value in super().actions():
            if color(observation, action, self.gamma, self.hash):
                value += self.delta
            else:
                value -= self.gamma * self.delta / (1 - self.gamma)

            actions.append((action, value))

        actions.sort(key=itemgetter(1), reverse=True)

        return actions
