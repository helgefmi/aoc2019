#!/usr/bin/env python3
from enum import Enum
from typing import List, Dict, Callable, Iterator, Generator, Tuple, Optional


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


class Tile(Enum):
    WALL = 0
    EMPTY = 1
    END = 2
    DEBUG = 3

    def to_char(self) -> str:
        chars = {
            Tile.EMPTY: '.',
            Tile.WALL: '#',
            Tile.END: '+',
            Tile.DEBUG: '\u001b[32m*\u001b[0m',
        }
        return chars[self]


Program = List[int]
Coord = Tuple[int, int]
Area = Dict[Coord, Tile]


def print_area(area: Area, robot_coord: Coord) -> None:
    xs = [coord[0] for coord in area]
    ys = [coord[1] for coord in area]

    min_y = min(ys)
    min_x = min(xs)

    height = max(ys) - min_y + 1
    width = max(xs) - min_x + 1

    rows = [[' ' for _ in range(width)] for __ in range(height)]
    for coord, tile in area.items():
        x, y = coord
        rows[y - min_y][x - min_x] = tile.to_char() if coord != robot_coord else '@'

    for row in rows[::-1]:
        print(''.join(row))


def str_to_prog(s: str) -> List[int]:
    return list(map(int, s.strip().split(',')))


class Intcode:
    def __init__(self, prog: Program, inputs: Iterator[int]):
        self.prog = prog[:] + [0] * (1024 * 1024 - len(prog))
        self.pc = 0
        self.inputs = iter(inputs)
        self.output = 0
        self.param_spec = 0
        self.rel_base = 0

    def get_param(self, is_write=False):
        ret = self.prog[self.pc]
        self.pc += 1

        addr_mode = self.param_spec % 10
        self.param_spec //= 10

        if not is_write:
            if addr_mode == 0:
                ret = self.prog[ret]
            elif addr_mode == 2:
                ret = self.prog[self.rel_base + ret]
        elif addr_mode == 2:
            ret = ret + self.rel_base

        return ret

    def iterable(self) -> Generator[int, int, None]:
        OPCODES: Dict[int, Callable[..., None]] = {
            1: self.op_add,
            2: self.op_multiply,
            3: self.op_input,
            4: self.op_output,
            5: self.op_jump_if_true,
            6: self.op_jump_if_false,
            7: self.op_less_than,
            8: self.op_equals,
            9: self.op_rel_base,
        }

        while True:
            opc = self.prog[self.pc]
            self.pc += 1

            opc, self.param_spec = opc % 100, opc // 100
            if opc == 99:
                print('halt')
                break

            fn = OPCODES[opc]

            fn()
            if opc == 4:
                yield self.output

    def op_add(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a + b

    def op_multiply(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a * b

    def op_input(self) -> None:
        a = self.get_param(is_write=True)
        self.prog[a] = next(self.inputs)

    def op_output(self) -> None:
        self.output = self.get_param()

    def op_jump_if_true(self) -> None:
        a = self.get_param()
        b = self.get_param()
        if a:
            self.pc = b

    def op_jump_if_false(self) -> None:
        a = self.get_param()
        b = self.get_param()
        if not a:
            self.pc = b

    def op_less_than(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a < b else 0

    def op_equals(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a == b else 0

    def op_rel_base(self) -> None:
        a = self.get_param()
        self.rel_base += a


def get_adjacent_coords(coord: Coord) -> List[Coord]:
    x, y = coord
    return [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]


def pathing(area: Area, from_coord: Coord, to_coord: Coord) -> Optional[List[Coord]]:
    open_coords = [from_coord]
    closed_coords = set()
    parents: Dict[Coord, Coord] = {}
    distances = {from_coord: 0}

    while open_coords:
        open_coords.sort(key=lambda coord: distances.get(coord, 1e10))
        current = open_coords.pop(0)

        if current == to_coord:
            break

        closed_coords.add(current)

        for child in get_adjacent_coords(current):
            if child in area and area[child] == Tile.WALL:
                continue

            if current not in area and child not in area:
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

    if to_coord not in parents:
        return None

    path: List[Coord] = []
    coord = to_coord
    while coord != from_coord:
        path.append(coord)
        coord = parents[coord]

    return path[::-1]


def delta_to_direction(from_coord: Coord, to_coord: Coord) -> Optional[Direction]:
    from_x, from_y = from_coord
    to_x, to_y = to_coord
    delta = (to_x - from_x, to_y - from_y)

    directions = {
        (0, 1): Direction.NORTH,
        (1, 0): Direction.EAST,
        (0, -1): Direction.SOUTH,
        (-1, 0): Direction.WEST,
    }

    return directions.get(delta, None)


def move(coord: Coord, direction: Direction) -> Coord:
    x, y = coord
    if direction == Direction.NORTH:
        return (x, y + 1)
    elif direction == Direction.EAST:
        return (x + 1, y)
    elif direction == Direction.SOUTH:
        return (x, y - 1)
    else:
        return (x - 1, y)


class Robot:
    def __init__(self, prog: Program):
        self.intc = Intcode(prog, self.get_inputs())

        self.robot_coord = (0, 0)
        self.next_coord: Optional[Coord] = None
        self.end_coord: Optional[Coord] = None
        self.area = {self.robot_coord: Tile.EMPTY}

        self.unexplored = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def get_inputs(self) -> Generator[int, None, None]:
        while True:
            coord = self.unexplored.pop()
            if self.area.get(coord, None) == Tile.WALL:
                continue

            direction = delta_to_direction(self.robot_coord, coord)
            if not direction:
                path = pathing(self.area, self.robot_coord, coord)
                if not path:
                    continue
                self.unexplored.append(coord)
                direction = delta_to_direction(self.robot_coord, path[0])

            assert direction
            self.next_coord = move(self.robot_coord, direction)

            yield direction.value

    def run(self) -> int:
        for output in self.intc.iterable():
            tile = Tile(output)
            assert self.next_coord
            self.area[self.next_coord] = tile

            if tile != Tile.WALL:
                self.robot_coord = self.next_coord

                for adjacent in get_adjacent_coords(self.robot_coord):
                    if adjacent not in self.area and adjacent not in self.unexplored:
                        self.unexplored.append(adjacent)

            if tile == Tile.END:
                self.end_coord = self.robot_coord

            self.next_coord = None

            if not self.unexplored:
                break

            print_area(self.area, self.robot_coord)
            print()

        if not self.end_coord:
            raise RuntimeError('No end coord')

        path = pathing(self.area, (0, 0), self.end_coord)
        assert path is not None

        for coord in path:
            self.area[coord] = Tile.DEBUG
        print_area(self.area, self.robot_coord)

        return len(path)


def compute(cts: str) -> int:
    prog = str_to_prog(cts)
    return Robot(prog).run()


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
