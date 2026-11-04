from pathlib import Path
from unittest import TestCase, main

from pigames import GoEngine, GNUGoEngine, KataGoEngine, matches
import numpy as np


class GoEngineTestCase(TestCase):
    OPENINGS_PATH = (
        Path(__file__).parent.parent
        / 'lib'
        / 'fuego-code'
        / 'book'
        / 'book.dat'
    )
    OPENINGS_LENGTH = 8

    def test_openings(self):
        with open(self.OPENINGS_PATH) as file:
            openings = GoEngine.openings(file, self.OPENINGS_LENGTH)

            self.assertEqual(
                next(openings),
                ('Q4', 'Q16', 'C4', 'D16', 'C14', 'F17', 'D10', 'F3'),
            )
            self.assertEqual(
                next(openings),
                ('Q4', 'Q16', 'C4', 'D16', 'C14', 'F17', 'J3', 'C15'),
            )
            self.assertEqual(len(list(openings)), 271)


class KataGoEngineTestCase(TestCase):
    ENGINE_PATH = Path(__file__).parent.parent / 'engines' / 'go' / 'katago'
    MODEL_PATH = (
        Path(__file__).parent.parent
        / 'engines'
        / 'go'
        / 'kata1.bin.gz'
    )
    CONFIG_PATH = (
        Path(__file__).parent.parent
        / 'engines'
        / 'go'
        / 'default_gtp.cfg'
    )
    MAX_VISITS = 500
    MIN_MAX_VISITS = 20
    MATCHES_COUNT = 2

    def test_perfect_play(self):
        engine1 = KataGoEngine(
            self.ENGINE_PATH,
            self.MODEL_PATH,
            self.CONFIG_PATH,
            max_visits=self.MAX_VISITS,
        )
        engine2 = KataGoEngine(
            self.ENGINE_PATH,
            self.MODEL_PATH,
            self.CONFIG_PATH,
            max_visits=self.MAX_VISITS,
        )

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2

        for _ in matches(engines, self.MATCHES_COUNT, progress=False):
            pass

        engine1.disconnect()
        engine2.disconnect()

    def test_imperfect_play(self):
        strong = KataGoEngine(
            self.ENGINE_PATH,
            self.MODEL_PATH,
            self.CONFIG_PATH,
            max_visits=self.MAX_VISITS,
        )
        weak = KataGoEngine(
            self.ENGINE_PATH,
            self.MODEL_PATH,
            self.CONFIG_PATH,
            max_visits=self.MIN_MAX_VISITS,
        )

        strong.connect()
        weak.connect()

        engines = strong, weak
        result = 1, 0

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            np.testing.assert_allclose(
                (np.array(m.result) + 0.5).clip(0, 1),
                result,
            )

        strong.disconnect()
        weak.disconnect()


class GNUGoEngineTestCase(TestCase):
    ENGINE_PATH = Path(__file__).parent.parent / 'engines' / 'go' / 'gnugo'
    MATCHES_COUNT = 2

    def test_perfect_play(self):
        engine1 = GNUGoEngine(self.ENGINE_PATH)
        engine2 = GNUGoEngine(self.ENGINE_PATH)

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2

        for _ in matches(engines, self.MATCHES_COUNT, progress=False):
            pass

        engine1.disconnect()
        engine2.disconnect()


if __name__ == '__main__':
    main()
