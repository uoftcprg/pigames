from pathlib import Path
from unittest import TestCase, main

from chess.engine import Limit
from pigames import ChessEngine, matches, WatermarkedEngine, z_scores


class WatermarkedEngineTestCase(TestCase):
    ENGINE_PATH = (
        Path(__file__).parent.parent
        / 'engines'
        / 'chess'
        / 'stockfish'
    )
    MULTI_PV = 3
    TIME = 1
    DELTA = 10
    MATCHES_COUNT = 2
    Z_THRESHOLD = 4

    def test_imperfect_play(self):
        original = ChessEngine(
            self.ENGINE_PATH,
            self.MULTI_PV,
            Limit(self.TIME),
        )
        watermarked = WatermarkedEngine(
            ChessEngine(
                self.ENGINE_PATH,
                self.MULTI_PV,
                Limit(self.TIME),
            ),
            self.DELTA,
        )

        original.connect()
        watermarked.connect()

        engines = original, watermarked
        ms = list(matches(engines, self.MATCHES_COUNT, progress=False))

        for m in ms:
            self.assertGreaterEqual(*m.result)

        original_z, watermarked_z = list(z_scores(ms))[-1]

        self.assertLess(abs(original_z), self.Z_THRESHOLD)
        self.assertGreaterEqual(watermarked_z, self.Z_THRESHOLD)
        original.disconnect()
        watermarked.disconnect()


if __name__ == '__main__':
    main()
