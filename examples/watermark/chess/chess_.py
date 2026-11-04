#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import asdict
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from random import seed, shuffle
from sys import stdout
from zipfile import ZipFile

from chess.engine import Limit
from jsonlines import Writer
from pigames import ChessEngine, matches, WatermarkedEngine


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('engine_path', type=Path)
    parser.add_argument('multi_pv', type=int)
    parser.add_argument('time', type=float)
    parser.add_argument('delta', type=float)
    parser.add_argument('gamma', type=Fraction)
    parser.add_argument('openings_path', type=Path)
    parser.add_argument('seed', type=int)
    parser.add_argument('matches_count', type=int)

    return parser.parse_args()


def main():
    args = parse_args()
    original = ChessEngine(args.engine_path, args.multi_pv, Limit(args.time))
    watermarked = WatermarkedEngine(
        ChessEngine(args.engine_path, args.multi_pv, Limit(args.time)),
        args.delta,
        args.gamma,
    )

    with ZipFile(args.openings_path) as zip_file:
        with zip_file.open(zip_file.namelist()[0]) as file:
            openings = list(ChessEngine.openings(TextIOWrapper(file)))

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
