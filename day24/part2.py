#!/usr/bin/env python3
from collections import defaultdict
from typing import Dict
from typing import Generator
from typing import List

import pytest

"""
- A bug dies (becoming an empty space) unless there is exactly one bug adjacent to it.

- An empty space becomes infested with a bug if exactly one or two bugs are adjacent to it.
"""

Area = Dict[int, List[str]]


def mk_area(width, height) -> Area:
    return defaultdict(lambda: [(' ' * width) for _ in range(height)])


def num_bugs(area: Area) -> int:
    ret = 0
    for scr in area.values():
        for row in scr:
            ret += sum(1 for c in row if c == '#')
    return ret


def get_adjacents(area: Area, level: int, x: int, y: int) -> Generator[str, None, None]:
    scr = area[level]

    height = len(scr)
    width = len(scr[0])

    map_inner = {
        (0, 1): [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
        (1, 0): [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
        (0, -1): [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
        (-1, 0): [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
    }

    for dir_x, dir_y in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        child_x = x + dir_x
        child_y = y + dir_y
        if child_x < 0:
            yield area[level + 1][2][1]
        elif child_x == width:
            yield area[level + 1][2][3]
        elif child_y < 0:
            yield area[level + 1][1][2]
        elif child_y == height:
            yield area[level + 1][3][2]
        elif (child_x, child_y) == (2, 2):
            for inner_x, inner_y in map_inner[(dir_x, dir_y)]:
                yield area[level - 1][inner_y][inner_x]
        else:
            yield scr[child_y][child_x]


def iterate(area: Area) -> Area:
    height = len(area[0])
    width = len(area[0][0])

    new_area = mk_area(width, height)

    for level, scr in list(area.items()):
        new_scr = []
        for y, row in enumerate(scr):
            new_row = ''
            for x, c in enumerate(row):
                if (x, y) == (2, 2):
                    new_row += '?'
                    continue
                adjacents = get_adjacents(area, level, x, y)
                num_adjacent_bugs = sum(1 for adjacent in adjacents if adjacent == '#')
                if c == '#':
                    new_row += '#' if num_adjacent_bugs == 1 else '.'
                else:
                    new_row += '#' if num_adjacent_bugs in [1, 2] else '.'
            new_scr.append(new_row)
        new_area[level] = new_scr
    return new_area


def compute(cts: str, num_iterations: int) -> int:
    scr = cts.splitlines()

    height = len(scr)
    width = len(scr[0])

    area: Area = mk_area(width, height)
    area[0] = scr

    for iteration in range(num_iterations):
        levels = sorted(area.keys())
        min_level, max_level = levels[0], levels[-1]
        if not all(c == '.' for c in ''.join(area[min_level])):
            area[min_level - 1]
        if not all(c == '.' for c in ''.join(area[max_level])):
            area[max_level + 1]

        area = iterate(area)

    return num_bugs(area)


INPUT_1 = """
....#
#..#.
#..##
..#..
#....
""".strip()


@pytest.mark.parametrize(
    'input_str, num_iterations, expected', [
        (INPUT_1, 10, 99),
    ]
)
def test_compute(input_str, num_iterations, expected) -> None:
    assert compute(input_str, num_iterations) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts, 200))

    return 0


if __name__ == '__main__':
    exit(main())
