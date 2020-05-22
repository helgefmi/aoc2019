#!/usr/bin/env python3
from copy import deepcopy
from typing import List, Tuple, Dict

import pytest

Area = List[List[str]]
Coord = Tuple[int, int]


def str_to_area(area_str):
    return [list(row) for row in area_str.splitlines()]


def find_stuff(area: Area):
    keys = {}
    doors = {}
    coords = (0, 0)
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if 'a' <= c <= 'z':
                keys[c] = (x, y)
            elif 'A' <= c <= 'Z':
                doors[c] = (x, y)
            elif c == '@':
                coords = (x, y)

    return coords, keys, doors


def get_adjacent_coords(coord: Coord) -> List[Coord]:
    x, y = coord
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def find_available_keys(area: Area, from_coord: Coord, keys):
    open_coords = [from_coord]
    closed_coords = set()
    parents: Dict[Coord, Coord] = {}
    distances = {from_coord: 0}

    while open_coords:
        open_coords.sort(key=lambda coord: distances.get(coord, 1e10))
        current = open_coords.pop(0)

        closed_coords.add(current)

        for child in get_adjacent_coords(current):
            x, y = child
            c = area[y][x]
            if c == '#' or 'A' <= c <= 'Z':
                continue

            if child in closed_coords:
                continue

            old_distance = distances.get(child, 1e10)
            new_distance = distances[current] + 1
            if new_distance < old_distance:
                distances[child] = new_distance
                parents[child] = current
            else:
                continue

            open_coords.append(child)

    for key_c, key_tuple in keys.items():
        if key_tuple in parents:
            path: List[Coord] = []
            coord = key_tuple
            while coord != from_coord:
                path.append(coord)
                coord = parents[coord]
            yield key_c, path


def compute(cts: str):
    area = str_to_area(cts)
    player, keys, doors = find_stuff(area)

    def recurse(area, player, keys, depth=0, mem={}):
        if not keys:
            return 0

        hash_key = hash((player, tuple(keys.keys())))
        if hash_key in mem:
            return mem[hash_key]

        keys_available = find_available_keys(area, player, keys)
        best_steps = 1e10
        for key_c, path in keys_available:
            new_keys = deepcopy(keys)
            key_x, key_y = new_keys.pop(key_c)

            new_area = deepcopy(area)
            new_area[key_y][key_x] = '.'

            if key_c.upper() in doors:
                door_x, door_y = doors[key_c.upper()]
                new_area[door_y][door_x] = '.'

            ret = recurse(new_area, (key_x, key_y), new_keys, depth + 1, mem)
            best_steps = min(ret + len(path), best_steps)

            if depth == 3:
                print(best_steps)

        mem[hash_key] = best_steps
        return best_steps

    return recurse(area, player, keys)


INPUT_1 = """
#########
#b.A.@.a#
#########
""".strip()

INPUT_2 = """
########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################
""".strip()

INPUT_3 = """
########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################
""".strip()

INPUT_4 = """
#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################
""".strip()

INPUT_5 = """
########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################
""".strip()


@pytest.mark.parametrize(
    'input_str, expected', [
        (INPUT_1, 8),
        (INPUT_2, 86),
        (INPUT_3, 132),
        (INPUT_4, 136),
        (INPUT_5, 81),
    ]
)
def test_compute(input_str, expected):
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
