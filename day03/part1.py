#!/usr/bin/env python3
import pytest

from typing import Dict, Callable, Tuple, List, Set

Position = Tuple[int, int]


DIR_UPDATES: Dict[str, Callable[[Position], Position]] = {
    'R': lambda p: (p[0], p[1] + 1),
    'L': lambda p: (p[0], p[1] - 1),
    'U': lambda p: (p[0] + 1, p[1]),
    'D': lambda p: (p[0] - 1, p[1]),
}


def manhattan_distance(pos: Position) -> int:
    x, y = pos
    return abs(x) + abs(y)


def compute_wire(wire: List[str]) -> Set[Position]:
    ret = set()
    pos = (0, 0)
    for instr in wire:
        direction, steps = instr[0], int(instr[1:])
        for _ in range(steps):
            pos = DIR_UPDATES[direction](pos)
            ret.add(pos)
    return ret


def compute(cts: str) -> int:
    wires = [line.split(',') for line in cts.strip().splitlines()]
    area_a, area_b = map(compute_wire, wires)

    intersections = area_a & area_b

    return min(map(manhattan_distance, intersections))


@pytest.mark.parametrize(
    'input_str, expected', [
        ('R8,U5,L5,D3\nU7,R6,D4,L4', 6),
        ('R75,D30,R83,U83,L12,D49,R71,U7,L72\nU62,R66,U55,R34,D71,R55,D58,R83', 159),
        ('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51\nU98,R91,D20,R16,D67,R40,U7,R15,U6,R7', 135),
    ]
)
def test_compute(input_str: str, expected: int) -> None:
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
