#!/usr/bin/env python3

from sys import stdin

from jsonlines import Reader
from pigames import Match, elo


def main():
    reader = Reader(stdin)

    print(elo(Match(**data) for data in reader))


if __name__ == '__main__':
    main()
