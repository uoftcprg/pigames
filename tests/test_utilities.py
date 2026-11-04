from unittest import TestCase, main

from pigames import elo


class UtilitiesTestCase(TestCase):
    def test_elo(self):
        self.assertEqual(
            str(elo(0, 10)),
            'Elo difference: -inf +/- nan, LOS: 0.1 %, DrawRatio: 0.0 %',
        )
        self.assertEqual(
            str(elo(10, 0)),
            'Elo difference: inf +/- nan, LOS: 99.9 %, DrawRatio: 0.0 %',
        )

        # Chess experiments

        self.assertEqual(
            str(elo(34, 31, 35)),
            'Elo difference: 10.4 +/- 55.4, LOS: 64.5 %, DrawRatio: 35.0 %',
        )
        self.assertEqual(
            str(elo(23, 26, 51)),
            'Elo difference: -10.4 +/- 48.0, LOS: 33.4 %, DrawRatio: 51.0 %',
        )
        self.assertEqual(
            str(elo(31, 28, 41)),
            'Elo difference: 10.4 +/- 52.7, LOS: 65.2 %, DrawRatio: 41.0 %',
        )
        self.assertEqual(
            str(elo(13, 11, 76)),
            'Elo difference: 6.9 +/- 33.4, LOS: 65.8 %, DrawRatio: 76.0 %',
        )
        self.assertEqual(
            str(elo(24, 18, 58)),
            'Elo difference: 20.9 +/- 44.3, LOS: 82.3 %, DrawRatio: 58.0 %',
        )
        self.assertEqual(
            str(elo(7, 14, 79)),
            'Elo difference: -24.4 +/- 31.1, LOS: 6.3 %, DrawRatio: 79.0 %',
        )

        # Ablation on gamma

        self.assertEqual(
            str(elo(12, 17, 71)),
            'Elo difference: -17.4 +/- 36.7, LOS: 17.7 %, DrawRatio: 71.0 %',
        )
        self.assertEqual(
            str(elo(7, 14, 79)),
            'Elo difference: -24.4 +/- 31.1, LOS: 6.3 %, DrawRatio: 79.0 %',
        )
        self.assertEqual(
            str(elo(13, 7, 80)),
            'Elo difference: 20.9 +/- 30.4, LOS: 91.0 %, DrawRatio: 80.0 %',
        )
        self.assertEqual(
            str(elo(13, 12, 75)),
            'Elo difference: 3.5 +/- 34.2, LOS: 57.9 %, DrawRatio: 75.0 %',
        )
        self.assertEqual(
            str(elo(14, 16, 70)),
            'Elo difference: -6.9 +/- 37.4, LOS: 35.8 %, DrawRatio: 70.0 %',
        )

        # Ablation on delta

        self.assertEqual(
            str(elo(7, 14, 79)),
            'Elo difference: -24.4 +/- 31.1, LOS: 6.3 %, DrawRatio: 79.0 %',
        )
        self.assertEqual(
            str(elo(10, 13, 77)),
            'Elo difference: -10.4 +/- 32.7, LOS: 26.6 %, DrawRatio: 77.0 %',
        )
        self.assertEqual(
            str(elo(7, 12, 81)),
            'Elo difference: -17.4 +/- 29.6, LOS: 12.6 %, DrawRatio: 81.0 %',
        )
        self.assertEqual(
            str(elo(20, 13, 67)),
            'Elo difference: 24.4 +/- 39.2, LOS: 88.8 %, DrawRatio: 67.0 %',
        )
        self.assertEqual(
            str(elo(32, 7, 61)),
            'Elo difference: 88.7 +/- 41.8, LOS: 100.0 %, DrawRatio: 61.0 %',
        )

        # Ablation on T

        self.assertEqual(
            str(elo(17, 18, 65)),
            'Elo difference: -3.5 +/- 40.5, LOS: 43.3 %, DrawRatio: 65.0 %',
        )
        self.assertEqual(
            str(elo(9, 10, 81)),
            'Elo difference: -3.5 +/- 29.8, LOS: 40.9 %, DrawRatio: 81.0 %',
        )
        self.assertEqual(
            str(elo(18, 15, 67)),
            'Elo difference: 10.4 +/- 39.3, LOS: 69.9 %, DrawRatio: 67.0 %',
        )
        self.assertEqual(
            str(elo(18, 11, 71)),
            'Elo difference: 24.4 +/- 36.7, LOS: 90.3 %, DrawRatio: 71.0 %',
        )
        self.assertEqual(
            str(elo(18, 15, 67)),
            'Elo difference: 10.4 +/- 39.3, LOS: 69.9 %, DrawRatio: 67.0 %',
        )
        self.assertEqual(
            str(elo(7, 14, 79)),
            'Elo difference: -24.4 +/- 31.1, LOS: 6.3 %, DrawRatio: 79.0 %',
        )

        # Go, Gomoku

        self.assertEqual(
            str(elo(47, 53, 0)),
            'Elo difference: -20.9 +/- 69.1, LOS: 27.4 %, DrawRatio: 0.0 %',
        )
        self.assertEqual(
            str(elo(47, 53, 0, asymptotic=True)),
            'Elo difference: -20.9 +/- 68.2, LOS: 27.4 %, DrawRatio: 0.0 %',
        )
        self.assertEqual(
            str(elo(44, 56, 0)),
            'Elo difference: -41.9 +/- 69.5, LOS: 11.5 %, DrawRatio: 0.0 %',
        )
        self.assertEqual(
            str(elo(44, 56, 0, asymptotic=True)),
            'Elo difference: -41.9 +/- 68.6, LOS: 11.5 %, DrawRatio: 0.0 %',
        )
        self.assertEqual(
            str(elo(47, 52, 1)),
            'Elo difference: -17.4 +/- 68.7, LOS: 30.8 %, DrawRatio: 1.0 %',
        )


if __name__ == '__main__':
    main()
