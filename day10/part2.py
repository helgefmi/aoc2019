#!/usr/bin/env python
import math
from collections import defaultdict
from typing import List, Tuple, Generator, Optional, Dict

import pytest


Coord = Tuple[int, int]
Area = List[List[str]]

NUMBERS = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def simplify(a: int, b: int) -> Coord:
    gcd = math.gcd(a, b)
    return (int(a / gcd), int(b / gcd))


def get_astroids(area: Area) -> Generator[Coord, None, None]:
    row: List[str]
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if c == '#':
                yield (y, x)


def find_x(area: Area) -> Optional[Coord]:
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if c == 'X':
                return (y, x)
    return None


def get_closest_collisions(coord: Coord, area: Area) -> List[Tuple[int, int]]:
    def manhattan(cmp_coord):
        return abs(coord[0] - cmp_coord[0]) + abs(coord[1] - cmp_coord[1])

    def circle_order(cmp_coord):
        y = cmp_coord[0] - coord[0]
        x = cmp_coord[1] - coord[1]
        return -math.atan2(x, y)

    closest: Dict[Coord, List[Coord]] = defaultdict(list)
    astroids = get_astroids(area)
    for coord2 in astroids:
        if coord2 == coord:
            continue

        simp = simplify(coord[0] - coord2[0], coord[1] - coord2[1])
        closest[simp].append(coord2)

    closest_sorted = [sorted(L, key=manhattan)[0] for L in closest.values()]
    closest_sorted.sort(key=circle_order)
    return closest_sorted


def get_ordered_astroids(area: Area) -> Generator[Coord, int, None]:
    coord = find_x(area)
    if coord is None:
        raise RuntimeError('No x')

    while any(c == '#' for row in area for c in row):
        collissions = get_closest_collisions(coord, area)
        for y, x in collissions:
            yield (y, x)
            area[y][x] = '.'


def compute(cts: str, nth: int) -> Optional[Coord]:
    area = [list(line) for line in cts.splitlines()]
    astroids = get_ordered_astroids(area)
    for i, a in enumerate(astroids, start=1):
        if i == nth:
            return a
    return None


TEST_1 = """
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
##...#.####X#####...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
""".strip()


@pytest.mark.parametrize(
    'nth, exp', [
        (1, (11, 12)),
        (2, (12, 1)),
        (3, (12, 2)),
        (10, (12, 8)),
        (20, (16, 0)),
        (50, (16, 9)),
        (100, (10, 16)),
        (199, (9, 6)),
        (200, (8, 2)),
        (201, (10, 9)),
        (299, (11, 1)),
    ]
)
def test_run_once(nth: int, exp: Coord) -> None:
    assert compute(TEST_1, nth) == (exp[1], exp[0])


def main() -> int:
    with open('day10.txt', 'r') as f:
        cts = f.read()

    ret = compute(cts, 200)
    if ret is None:
        raise RuntimeError("Compute didn't return")
    print(ret, ret[1] * 100 + ret[0])

    return 0


if __name__ == '__main__':
    exit(main())
