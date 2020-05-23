#!/usr/bin/env python3
from collections import defaultdict

import pytest


def parse_screen(area):
    assert len(set(len(row) for row in area)) == 1

    # populate `portals`
    portals = defaultdict(list)
    for y in range(1, len(area) - 1):
        for x in range(1, len(area[y]) - 1):
            left, c, right = area[y][x - 1:x + 2]
            top = area[y - 1][x]
            bot = area[y + 1][x]

            if c.isupper():
                if left.isupper() and right == '.':
                    portals[left + c].append(((x, y), (x + 1, y)))
                elif right.isupper() and left == '.':
                    portals[c + right].append(((x, y), (x - 1, y)))

                elif top.isupper() and bot == '.':
                    portals[top + c].append(((x, y), (x, y + 1)))
                elif bot.isupper() and top == '.':
                    portals[c + bot].append(((x, y), (x, y - 1)))

    # find player/finish and remove from `portals` since they're one-way only.
    player = portals.pop('AA')[0][1]
    finish = portals.pop('ZZ')[0][1]

    assert all(len(data) == 2 for data in portals.values())

    # restructure for pathing algorithm
    transfers = {}
    for data in portals.values():
        transfers[data[0][0]] = data[1][1]
        transfers[data[1][0]] = data[0][1]

    return player, finish, transfers


def get_adjacent_coords(coord):
    x, y = coord
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def pathing(area, from_coord, end_coord, transfers):
    open_coords = [from_coord]
    closed_coords = set()
    parents = {}
    distances = {from_coord: 0}

    while open_coords:
        open_coords.sort(key=lambda coord: distances.get(coord, 1e10))
        current = open_coords.pop(0)

        closed_coords.add(current)

        for child in get_adjacent_coords(current):
            child = transfers.get(child, child)

            x, y = child
            c = area[y][x]

            if c != '.':
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

    path = []
    coord = end_coord
    while coord != from_coord:
        path.append(coord)
        coord = parents[coord]
    return path[::-1]


def compute(cts: str):
    area = [list(row) for row in cts.splitlines()]
    player, finish, transfers = parse_screen(area)

    path = pathing(area, player, finish, transfers)

    return len(path)


INPUT_1 = """\
         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       \
""" # noqa

INPUT_2 = """\
                   A               
                   A               
  #################.#############  
  #.#...#...................#.#.#  
  #.#.#.###.###.###.#########.#.#  
  #.#.#.......#...#.....#.#.#...#  
  #.#########.###.#####.#.#.###.#  
  #.............#.#.....#.......#  
  ###.###########.###.#####.#.#.#  
  #.....#        A   C    #.#.#.#  
  #######        S   P    #####.#  
  #.#...#                 #......VT
  #.#.#.#                 #.#####  
  #...#.#               YN....#.#  
  #.###.#                 #####.#  
DI....#.#                 #.....#  
  #####.#                 #.###.#  
ZZ......#               QG....#..AS
  ###.###                 #######  
JO..#.#.#                 #.....#  
  #.#.#.#                 ###.#.#  
  #...#..DI             BU....#..LF
  #####.#                 #.#####  
YN......#               VT..#....QG
  #.###.#                 #.###.#  
  #.#...#                 #.....#  
  ###.###    J L     J    #.#.###  
  #.....#    O F     P    #.#...#  
  #.###.#####.#.#####.#####.###.#  
  #...#.#.#...#.....#.....#.#...#  
  #.#####.###.###.#.#.#########.#  
  #...#.#.....#...#.#.#.#.....#.#  
  #.###.#####.###.###.#.#.#######  
  #.#.........#...#.............#  
  #########.###.###.#############  
           B   J   C               
           U   P   P               \
""" # noqa


@pytest.mark.parametrize(
    'input_str, expected', [
        (INPUT_1, 23),
        (INPUT_2, 58),
    ]
)
def test_compute(input_str, expected):
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
