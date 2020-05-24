#!/usr/bin/env python3
from typing import Generator
from typing import List

import pytest

"""
- A bug dies (becoming an empty space) unless there is exactly one bug adjacent to it.

- An empty space becomes infested with a bug if exactly one or two bugs are adjacent to it.
"""

Screen = List[str]


def screen_hash(scr: Screen) -> int:
    return hash('\n'.join(scr))


def biodiversity_rating(scr: Screen) -> int:
    ret = 0
    for y, row in enumerate(scr):
        for x, c in enumerate(row):
            i = y * len(scr[0]) + x
            if c == '#':
                ret += 2 ** i
    return ret


def get_adjacents(scr: Screen, x: int, y: int) -> Generator[str, None, None]:
    height = len(scr)
    width = len(scr[0])

    for dir_x, dir_y in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        child_x = x + dir_x
        child_y = y + dir_y
        if not (0 <= child_x < width):
            yield '.'
        elif not (0 <= child_y < height):
            yield '.'
        else:
            yield scr[child_y][child_x]


def iterate(scr: Screen) -> Screen:
    new_scr = []
    for y, row in enumerate(scr):
        new_row = ''
        for x, c in enumerate(row):
            adjacents = get_adjacents(scr, x, y)
            num_adjacent_bugs = sum(1 for adjacent in adjacents if adjacent == '#')
            if c == '#':
                new_row += '#' if num_adjacent_bugs == 1 else '.'
            else:
                new_row += '#' if num_adjacent_bugs in [1, 2] else '.'
        new_scr.append(new_row)
    return new_scr


def compute(cts: str) -> int:
    scr = cts.splitlines()

    mem = set()
    while True:
        key = screen_hash(scr)
        if key in mem:
            return biodiversity_rating(scr)
        mem.add(key)

        scr = iterate(scr)

    raise RuntimeError('unreachable')


INPUT_1 = """
....#
#..#.
#..##
..#..
#....
""".strip()


@pytest.mark.parametrize(
    'input_str, expected', [
        (INPUT_1, 2129920),
    ]
)
def test_compute(input_str, expected) -> None:
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
