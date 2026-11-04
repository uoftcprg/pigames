from io import TextIOWrapper
from pathlib import Path
from unittest import TestCase, main
from zipfile import ZipFile

from chess.engine import Limit
from pigames import ChessEngine, matches
import numpy as np


class ChessEngineTestCase(TestCase):
    OPENINGS_PATH = (
        Path(__file__).parent.parent
        / 'lib'
        / 'books'
        / '8moves_v3.pgn.zip'
    )

    def test_openings(self):
        with ZipFile(self.OPENINGS_PATH) as zip_file:
            with zip_file.open(zip_file.namelist()[0]) as file:
                openings = ChessEngine.openings(TextIOWrapper(file))

                self.assertEqual(
                    next(openings),
                    (
                        'g1f3',
                        'd7d5',
                        'g2g3',
                        'c7c6',
                        'f1g2',
                        'g8f6',
                        'd2d3',
                        'c8g4',
                        'h2h3',
                        'g4h5',
                        'b2b3',
                        'e7e6',
                        'c1b2',
                        'd8a5',
                        'd1d2',
                        'a5d2',
                    ),
                )
                self.assertEqual(
                    next(openings),
                    (
                        'd2d4',
                        'g8f6',
                        'c2c4',
                        'e7e6',
                        'g1f3',
                        'b7b6',
                        'g2g3',
                        'c8a6',
                        'd1a4',
                        'a6b7',
                        'f1g2',
                        'c7c5',
                        'd4c5',
                        'f8c5',
                        'e1g1',
                        'c5e7',
                    ),
                )
                self.assertEqual(len(list(openings)), 34698)

    ENGINE_PATH = (
        Path(__file__).parent.parent
        / 'engines'
        / 'chess'
        / 'stockfish'
    )
    DEPTH = 20
    MIN_DEPTH = 1
    MATCHES_COUNT = 2

    def test_perfect_play(self):
        engine1 = ChessEngine(self.ENGINE_PATH, limit=Limit(depth=self.DEPTH))
        engine2 = ChessEngine(self.ENGINE_PATH, limit=Limit(depth=self.DEPTH))

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2
        assertions = self.assertGreaterEqual, self.assertLessEqual

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            assertions[0](*m.result)

            assertions = assertions[::-1]

        engine1.disconnect()
        engine2.disconnect()

    def test_imperfect_play(self):
        strong = ChessEngine(self.ENGINE_PATH, limit=Limit(depth=self.DEPTH))
        weak = ChessEngine(self.ENGINE_PATH, limit=Limit(depth=self.MIN_DEPTH))

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
