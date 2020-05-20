#!/usr/bin/env python3
from __future__ import annotations

import pytest
from itertools import combinations
from typing import List


class Vector:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
        self. x = x
        self. y = y
        self. z = z

    def __str__(self):
        return 'x={}, y={}, z={}'.format(self.x, self.y, self.z)


class Moon:
    def __init__(self, pos: Vector, vel: Vector) -> None:
        self.pos = pos
        self.vel = vel

    def __str__(self):
        return 'pos=<{}>, vel=<{}>'.format(self.pos, self.vel)


def compute(moons: List[Moon], num_iterations: int, print_steps: bool = False) -> int:
    if print_steps:
        print('Step 0')
        print('\n'.join(str(moon) for moon in moons))

    moon_combinations = list(combinations(moons, 2))

    for step in range(num_iterations):
        for m1, m2 in moon_combinations:
            acc_x = (m1.pos.x < m2.pos.x) - (m1.pos.x > m2.pos.x)
            acc_y = (m1.pos.y < m2.pos.y) - (m1.pos.y > m2.pos.y)
            acc_z = (m1.pos.z < m2.pos.z) - (m1.pos.z > m2.pos.z)

            m1.vel.x += acc_x
            m2.vel.x -= acc_x

            m1.vel.y += acc_y
            m2.vel.y -= acc_y

            m1.vel.z += acc_z
            m2.vel.z -= acc_z

        for moon in moons:
            moon.pos.x += moon.vel.x
            moon.pos.y += moon.vel.y
            moon.pos.z += moon.vel.z

        if print_steps:
            print('Step', step + 1)
            print('\n'.join(str(moon) for moon in moons))

    pot = [abs(m.pos.x) + abs(m.pos.y) + abs(m.pos.z) for m in moons]
    kin = [abs(m.vel.x) + abs(m.vel.y) + abs(m.vel.z) for m in moons]
    return sum(a * b for a, b in zip(pot, kin))


INPUT_1 = [
    Moon(Vector(-1, 0, 2), Vector()),
    Moon(Vector(2, -10, -7), Vector()),
    Moon(Vector(4, -8, 8), Vector()),
    Moon(Vector(3, 5, -1), Vector()),
]

INPUT_2 = [
    Moon(Vector(-8, -10, 0), Vector()),
    Moon(Vector(5, 5, 10), Vector()),
    Moon(Vector(2, -7, 3), Vector()),
    Moon(Vector(9, -8, -3), Vector()),
]


@pytest.mark.parametrize(
    'moons, num_iterations, expected', [
        (INPUT_1, 10, 179),
        (INPUT_2, 100, 1940),
    ]
)
def test_compute(moons: List[Moon], num_iterations: int, expected: int) -> None:
    assert compute(moons, num_iterations, True) == expected


def main() -> int:
    moons = [
        Moon(Vector(-3, 15, -11), Vector()),
        Moon(Vector(3, 13, -19), Vector()),
        Moon(Vector(-13, 18, -2), Vector()),
        Moon(Vector(6, 0, -1), Vector()),
    ]

    print(compute(moons, 1000))

    return 0


if __name__ == '__main__':
    exit(main())
