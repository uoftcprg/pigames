from unittest import TestCase, main

from pigames import elo, matches, TicTacToeEngine, WorstEngine
import numpy as np


class TicTacToeTestCase(TestCase):
    OPENINGS_LENGTH = 4

    def test_openings(self):
        book = TicTacToeEngine().openings(self.OPENINGS_LENGTH)

        self.assertEqual(next(book), ('0', '4', '1', '2'))
        self.assertEqual(next(book), ('0', '4', '2', '1'))
        self.assertEqual(len(list(book)), 286)

    MATCHES_COUNT = 5

    def test_perfect_play(self):
        engine1 = TicTacToeEngine()
        engine2 = TicTacToeEngine()

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2
        result = 0.5, 0.5

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        result = 1, 0

        for m in matches(
                engines,
                self.MATCHES_COUNT,
                [['0', '4', '8', '2'], ['0', '2']],
                progress=False,
        ):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        engine1.disconnect()
        engine2.disconnect()

    def test_imperfect_play(self):
        strong = TicTacToeEngine()
        weak = WorstEngine(TicTacToeEngine())

        strong.connect()
        weak.connect()

        engines = strong, weak

        self.assertEqual(
            str(elo(matches(engines, self.MATCHES_COUNT, progress=False))),
            'Elo difference: inf +/- nan, LOS: 99.9 %, DrawRatio: 0.0 %',
        )
        strong.disconnect()
        weak.disconnect()


if __name__ == '__main__':
    main()
