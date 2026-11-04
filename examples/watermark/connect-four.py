#!/usr/bin/env python3

from argparse import ArgumentParser
from fractions import Fraction
from dataclasses import asdict
from random import seed, shuffle
from sys import stdout

from jsonlines import Writer
from pigames import ConnectFourEngine, matches, WatermarkedEngine


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('delta', type=float)
    parser.add_argument('gamma', type=Fraction)
    parser.add_argument('openings_count', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('matches_count', type=int)

    return parser.parse_args()


def main():
    args = parse_args()
    original = ConnectFourEngine()
    watermarked = WatermarkedEngine(
        ConnectFourEngine(),
        args.delta,
        args.gamma,
    )
    openings = list(ConnectFourEngine.openings(args.openings_count))

    seed(args.seed)
    shuffle(openings)

    original.connect()
    watermarked.connect()

    engines = original, watermarked
    writer = Writer(stdout, flush=True)

    for m in matches(engines, args.matches_count, openings, reconnect=True):
        writer.write(asdict(m))

    original.disconnect()
    watermarked.disconnect()


if __name__ == '__main__':
    main()
