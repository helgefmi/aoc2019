#!/usr/bin/env python
import math
from collections import defaultdict
from typing import List, Tuple, Generator

import pytest


def simplify(a, b):
    gcd = math.gcd(a, b)
    return (a / gcd, b / gcd)


def get_astroids(area: List[str]) -> Generator[Tuple[int, int], None, None]:
    row: str
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if c == '.':
                continue
            yield (y, x)


def get_collisions(coord: Tuple[int, int], area: List[str]) -> List[Tuple[int, int]]:
    closest = defaultdict(list)
    for coord2 in get_astroids(area):
        if coord2 == coord:
            continue

        simp = simplify(coord2[0] - coord[0], coord2[1] - coord[1])
        if simp not in closest:
            closest[simp].append(coord2)

    return [sorted(L)[0] for L in closest.values()]


def compute(cts: str) -> int:
    area = cts.splitlines()
    best = 0
    for coord in get_astroids(area):
        collissions = get_collisions(coord, area)
        if len(collissions) > best:
            print(coord, len(collissions))
        best = max(best, len(collissions))
    return best


TEST_0 = """
.#..#
.....
#####
....#
...##
""".strip()

TEST_1 = """
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
""".strip()

TEST_2 = """
#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.
""".strip()

TEST_3 = """
.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..
""".strip()

TEST_4 = """
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
""".strip()

TEST_5 = """
.#....#####...#..
##...##.#####..##
##...#...#.#####.
..#.....X...###..
..#.#.....#....##
""".strip()


@pytest.mark.parametrize(
    'inp, exp', [
        (TEST_0, 8),
        (TEST_1, 33),
        (TEST_2, 35),
        (TEST_3, 41),
        (TEST_4, 210),
        (TEST_5, 30),
    ]
)
def test_run_once(inp: str, exp: int) -> None:
    assert compute(inp) == exp


def main() -> int:
    with open('day10.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
