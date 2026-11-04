from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial, singledispatch
from itertools import cycle, islice, permutations, starmap
from math import erf, inf, isclose, log, log10, sqrt
from operator import getitem, lt

from scipy.stats import norm
from tqdm import tqdm


@dataclass
class Match:
    indices: list[int]
    observations: list[str]
    actions: list[str]
    result: tuple[float, ...]


def match(engines, opening=()):

    def observe():
        observation = engines[0].observe()

        assert all(engine.observe() == observation for engine in engines[1:])

        return observation

    for engine in engines:
        engine.reset()

    for action in opening:
        for engine in engines:
            engine.play(action)

    indices = []
    observations = []
    actions = []

    for index, engine in cycle(enumerate(engines)):
        observation = observe()
        action_values = engine.actions()

        if not action_values:
            break

        action = action_values[0][0]

        indices.append(index)
        observations.append(observation)
        actions.append(action)

        for engine in engines:
            engine.play(action)

    result = engines[0].result()

    for engine in engines[1:]:
        if not all(starmap(isclose, zip(engine.result(), result))):
            raise ValueError('inconsistent results')

    match = Match(indices, observations, actions, result)

    return match


def matches(
        engines,
        count,
        openings=((),),
        progress=True,
        reconnect=False,
):
    engine_count = len(engines)
    indices = range(engine_count)
    openings = islice(cycle(openings), count)

    if progress:
        openings = tqdm(openings, total=count)

    for opening in openings:
        for indices2 in permutations(indices):
            if reconnect:
                for engine in engines:
                    engine.disconnect()
                    engine.connect()

            engines2 = tuple(map(partial(getitem, engines), indices2))
            m = match(engines2, opening)
            m.indices = list(map(partial(getitem, indices2), m.indices))
            m.result = tuple(
                map(
                    partial(getitem, m.result),
                    map(indices2.index, indices),
                ),
            )

            yield m


@dataclass
class Elo:
    elo_difference: tuple[float, float]
    likelihood_of_superiority: float
    draw_ratio: float

    def __str__(self):
        return (
            f'Elo difference: {self.elo_difference[0]:.1f} '
            f'+/- {self.elo_difference[1]:.1f}, '
            f'LOS: {self.likelihood_of_superiority * 100:.1f} %, '
            f'DrawRatio: {self.draw_ratio * 100:.1f} %'
        )


@singledispatch
def elo(W, L, D=0, alpha=0.05, asymptotic=False):
    z = norm.ppf(1 - alpha / 2)

    def delta(mu):
        if isclose(mu, 0):
            delta = -inf
        elif isclose(mu, 1):
            delta = inf
        else:
            delta = -400 * log10(1 / mu - 1)

        return delta

    n = W + L + D
    mu = (W + D / 2) / n
    sigma_squared = (
        W * (1 - mu) ** 2
        + L * (0 - mu) ** 2
        + D * (0.5 - mu) ** 2
    ) / n
    sigma = sqrt(sigma_squared)

    if asymptotic:
        pm = 400 * z * sigma / (log(10) * sqrt(n) * mu * (1 - mu))
    else:
        s = sigma / sqrt(n)
        pm = (delta(mu + z * s) - delta(mu - z * s)) / 2

    return Elo(
        (delta(mu), pm),
        (1 + erf((W - L) / sqrt(2 * (W + L)))) / 2 if W + L else 0.5,
        D / n,
    )


@elo.register(Iterable)
def _(matches, alpha=0.05, asymptotic=False):
    W = 0
    L = 0
    D = 0

    for m in matches:
        if isclose(*m.result):
            D += 1
        elif lt(*m.result):
            L += 1
        else:
            W += 1

    return elo(W, L, D, alpha, asymptotic)
