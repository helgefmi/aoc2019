#!/usr/bin/env python3
from __future__ import annotations

import math
import pytest
from functools import reduce
from itertools import count, combinations


def transpose(arr):
    return [list(part) for part in zip(*arr)]


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)


def compute_axis(pos):
    num_moons = len(pos)
    initial_pos = pos[:]

    vel = [0] * num_moons
    initial_vel = vel[:]

    i_combs = list(combinations(range(num_moons), 2))

    for step in count(1):
        for i1, i2 in i_combs:
            acc = (pos[i2] > pos[i1]) - (pos[i2] < pos[i1])
            vel[i1] += acc
            vel[i2] -= acc

        for i in range(num_moons):
            pos[i] += vel[i]

        if pos == initial_pos and vel == initial_vel:
            break

    return step


def compute(pos):
    steps = map(compute_axis, transpose(pos))
    return reduce(lcm, steps)


INPUT_1 = [
    [-1, 0, 2],
    [2, -10, -7],
    [4, -8, 8],
    [3, 5, -1],
]

INPUT_2 = [
    [-8, -10, 0],
    [5, 5, 10],
    [2, -7, 3],
    [9, -8, -3],
]


@pytest.mark.parametrize(
    'moons, expected', [
        (INPUT_1, 2772),
        (INPUT_2, 4686774924),
    ]
)
def test_compute(moons, expected: int) -> None:
    assert compute(moons) == expected


def main() -> int:
    moons = [
        [-3, 15, -11],
        [3, 13, -19],
        [-13, 18, -2],
        [6, 0, -1],
    ]

    print(compute(moons))

    return 0


if __name__ == '__main__':
    exit(main())
