#!/usr/bin/env python3
from typing import List, Tuple, Dict

import pytest

Area = List[List[str]]
Coord = Tuple[int, int]


def str_to_area(area_str):
    return [list(row) for row in area_str.splitlines()]


def find_stuff(area: Area):
    keys = {}
    doors = {}
    player = (0, 0)
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if 'a' <= c <= 'z':
                keys[c] = (x, y)
            elif 'A' <= c <= 'Z':
                doors[c] = (x, y)
            elif c == '@':
                player = (x, y)

    return player, keys, doors


def get_adjacent_coords(coord: Coord) -> List[Coord]:
    x, y = coord
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def find_keys_and_doors(area: Area, from_coord: Coord, keys, doors):
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

            if c == '#' or child in closed_coords:
                continue

            old_distance = distances.get(child, 1e10)
            new_distance = distances[current] + 1
            if new_distance < old_distance:
                distances[child] = new_distance
                parents[child] = current
            else:
                continue

            open_coords.append(child)

    useful_paths = {}
    coords = list(keys.values()) + list(doors.values())
    for coord in coords:
        if coord in parents:
            path: List[Coord] = []
            keys_needed = ''
            it = coord
            while it != from_coord:
                x, y = it
                if area[y][x].isupper():
                    keys_needed += area[y][x].lower()
                path.append(it)
                it = parents[it]
            useful_paths[coord] = (len(path), keys_needed)

    return useful_paths


def find_reachable_keys(keys, collected_keys, paths):
    for key_c, key_tuple in keys.items():
        if key_c in collected_keys:
            continue

        steps, keys_needed = paths[key_tuple]
        if any(key not in collected_keys for key in keys_needed):
            continue

        yield (key_c, steps)


def get_useful_paths(area, keys, doors, player):
    ret = {}
    starting_coords = list(keys.values()) + list(doors.values()) + [player]
    for coord in starting_coords:
        ret[coord] = find_keys_and_doors(area, coord, keys, doors)
    return ret


def compute(cts: str):
    area = str_to_area(cts)
    player, keys, doors = find_stuff(area)

    useful_paths = get_useful_paths(area, keys, doors, player)

    max_depth = len(keys)

    def recurse(player, collected_keys='', depth=0, mem={}):
        if depth == max_depth:
            return 0

        hash_key = hash((player, tuple(sorted(collected_keys))))
        if hash_key in mem:
            return mem[hash_key]

        reachable_keys = find_reachable_keys(keys, collected_keys, useful_paths[player])

        best_steps = 1e10
        for key_c, steps in reachable_keys:
            key_tuple = keys[key_c]
            ret = recurse(key_tuple, collected_keys + key_c, depth + 1, mem)
            best_steps = min(ret + steps, best_steps)

        mem[hash_key] = best_steps
        return best_steps

    return recurse(player)


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
