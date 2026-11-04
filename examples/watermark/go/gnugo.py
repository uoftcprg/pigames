#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from random import seed, shuffle
from sys import stdout

from jsonlines import Writer
from pigames import GNUGoEngine, GoEngine, matches, WatermarkedEngine


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('engine_path', type=Path)
    parser.add_argument('delta', type=float)
    parser.add_argument('gamma', type=Fraction)
    parser.add_argument('openings_path', type=Path)
    parser.add_argument('openings_length', type=int)
    parser.add_argument('seed', type=int)
    parser.add_argument('matches_count', type=int)

    return parser.parse_args()


def main():
    args = parse_args()
    original = GNUGoEngine(args.engine_path)
    watermarked = WatermarkedEngine(
        GNUGoEngine(args.engine_path),
        args.delta,
        args.gamma,
    )

    with open(args.openings_path) as file:
        openings = list(GoEngine.openings(file, args.openings_length))

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
