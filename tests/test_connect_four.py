from unittest import TestCase, main

from pigames import ConnectFourEngine, matches, WorstEngine
import numpy as np


class ConnectFourEngineTestCase(TestCase):
    OPENINGS_LENGTH = 8

    def test_openings(self):
        book = ConnectFourEngine().openings(self.OPENINGS_LENGTH)

        self.assertEqual(next(book), ('3', '0', '2', '0', '0', '0', '0', '0'))
        self.assertEqual(next(book), ('3', '0', '2', '0', '0', '0', '0', '1'))
        self.assertEqual(len(list(book)), 127688)

    MATCHES_COUNT = 2

    def test_perfect_play(self):
        engine1 = ConnectFourEngine()
        engine2 = ConnectFourEngine()

        engine1.connect()
        engine2.connect()

        engines = engine1, engine2
        result = 1, 0

        for m in matches(engines, self.MATCHES_COUNT, progress=False):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        result = 0.5, 0.5

        for m in matches(
                engines,
                self.MATCHES_COUNT,
                [['2'], ['4']],
                progress=False,
        ):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        result = 0, 1

        for m in matches(
                engines,
                self.MATCHES_COUNT,
                [['0'], ['1'], ['5'], ['6']],
                progress=False,
        ):
            np.testing.assert_allclose(m.result, result)

            result = result[::-1]

        engine1.disconnect()
        engine2.disconnect()

    def test_imperfect_play(self):
        strong = ConnectFourEngine()
        weak = WorstEngine(ConnectFourEngine())

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
