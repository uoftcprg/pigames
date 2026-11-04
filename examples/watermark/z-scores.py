#!/usr/bin/env python3

from sys import stdin

from jsonlines import Reader
from pigames import Match, z_scores


def main():
    reader = Reader(stdin)

    for zs in z_scores(Match(**data) for data in reader):
        print(*zs)


if __name__ == '__main__':
    main()
