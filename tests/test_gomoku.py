from pathlib import Path
from unittest import TestCase, main

from pigames import GomokuEngine, matches, RapfiEngine
import numpy as np


class GomokuTestCase(TestCase):
    OPENINGS_PATH = (
        Path(__file__).parent.parent
        / 'lib'
        / 'gomocup-results'
        / 'gomocup2026results'
        / 'openings_standard15_piskvork.txt'
    )

    def test_openings(self):
        with open(self.OPENINGS_PATH) as file:
            openings = GomokuEngine.openings(file)

            self.assertEqual(
                next(openings),
                ('6,6', '4,4', '6,2', '2,4', '3,2', '5,4', '3,4'),
            )
            next(openings)
            self.assertEqual(
                next(openings),
                ('10,5', '10,4', '10,3', '11,2', '13,2'),
            )
            self.assertEqual(len(list(openings)), 9)


class RapfiEngineTestCase(TestCase):
    ENGINE_PATH = (
        Path(__file__).parent.parent
        / 'engines'
        / 'gomoku'
        / 'pbrain-rapfi'
    )
    MAX_DEPTH = 20
    MIN_MAX_DEPTH = 1
    MATCHES_COUNT = 2

    def test_perfect_play(self):
        engine1 = RapfiEngine(self.ENGINE_PATH, max_depth=self.MAX_DEPTH)
        engine2 = RapfiEngine(self.ENGINE_PATH, max_depth=self.MAX_DEPTH)

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2
        result = 1, 0

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        engine1.disconnect()
        engine2.disconnect()

    def test_imperfect_play(self):
        strong = RapfiEngine(self.ENGINE_PATH, max_depth=self.MAX_DEPTH)
        weak = RapfiEngine(self.ENGINE_PATH, max_depth=self.MIN_MAX_DEPTH)

        strong.connect()
        weak.connect()

        engines = strong, weak
        result = 1, 0

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            np.testing.assert_allclose(m.result, result)

        strong.disconnect()
        weak.disconnect()


if __name__ == '__main__':
    main()
