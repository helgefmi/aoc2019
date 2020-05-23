#!/usr/bin/env python3
from copy import deepcopy
from typing import List, Tuple, Dict

import pytest

Area = List[List[str]]
Coord = Tuple[int, int]


def str_to_area(area_str: str) -> Area:
    return [list(row) for row in area_str.splitlines()]


def parse_screen(area: Area) -> Tuple[List[Coord], Dict[str, Coord], Dict[str, Coord]]:
    keys = {}
    doors = {}
    players = []
    for y, row in enumerate(area):
        for x, c in enumerate(row):
            if 'a' <= c <= 'z':
                keys[c] = (x, y)
            elif 'A' <= c <= 'Z':
                doors[c] = (x, y)
            elif c == '@':
                players.append((x, y))

    return players, keys, doors


def get_adjacent_coords(coord: Coord) -> List[Coord]:
    x, y = coord
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def find_keys_and_doors(area: Area, from_coord: Coord, keys, doors) -> Dict[Coord, Tuple[int, str]]:
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


def find_reachable_keys(keys: Dict[str, List[Coord]], collected_keys: str, paths):
    for key_c, key_tuple in keys.items():
        if key_c in collected_keys:
            continue

        if key_tuple not in paths:
            continue

        steps, keys_needed = paths[key_tuple]
        if any(key not in collected_keys for key in keys_needed):
            continue

        yield (key_c, steps)


def get_useful_paths(area, keys, doors, players):
    ret = {}
    starting_coords = list(keys.values()) + list(doors.values()) + players
    for coord in starting_coords:
        ret[coord] = find_keys_and_doors(area, coord, keys, doors)
    return ret


def compute(cts: str):
    area = str_to_area(cts)
    players, keys, doors = parse_screen(area)

    useful_paths = get_useful_paths(area, keys, doors, players)

    max_depth = len(keys)

    def recurse(players, collected_keys='', depth=0, mem={}):
        if depth == max_depth:
            return 0

        hash_key = hash((tuple(players), tuple(sorted(collected_keys))))
        if hash_key in mem:
            return mem[hash_key]

        best_steps = 1e10
        for player_i, player in enumerate(players):
            reachable_keys = find_reachable_keys(keys, collected_keys, useful_paths[player])
            for key_c, steps in reachable_keys:
                new_players = deepcopy(players)
                new_players[player_i] = keys[key_c]
                ret = recurse(new_players, collected_keys + key_c, depth + 1, mem)
                best_steps = min(ret + steps, best_steps)

        mem[hash_key] = best_steps
        return best_steps

    return recurse(players)


INPUT_1 = """
#######
#a.#Cd#
##@#@##
#######
##@#@##
#cB#Ab#
#######
""".strip()

INPUT_2 = """
###############
#d.ABC.#.....a#
######@#@######
###############
######@#@######
#b.....#.....c#
###############
""".strip()

INPUT_3 = """
#############
#DcBa.#.GhKl#
#.###@#@#I###
#e#d#####j#k#
###C#@#@###J#
#fEbA.#.FgHi#
#############
""".strip()

INPUT_4 = """
#############
#g#f.D#..h#l#
#F###e#E###.#
#dCba@#@BcIJ#
#############
#nK.L@#@G...#
#M###N#H###.#
#o#m..#i#jk.#
#############
""".strip()


@pytest.mark.parametrize(
    'input_str, expected', [
        (INPUT_1, 8),
        (INPUT_2, 24),
        (INPUT_3, 32),
        (INPUT_4, 72),
    ]
)
def test_compute(input_str, expected):
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

        area = [list(row) for row in cts.splitlines()]
        for y in range(39, 42):
            for x in range(39, 42):
                area[y][x] = '@' if y % 2 == 1 and x % 2 == 1 else '#'
        cts = '\n'.join(''.join(row) for row in area)

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
