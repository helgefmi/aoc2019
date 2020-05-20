#!/usr/bin/env python3
from collections import defaultdict

from typing import Dict, Set

import pytest


def num_orbits(obj, orbits: Dict[str, Set[str]], mem: Dict[str, int]) -> int:
    if obj == 'COM':
        return 0

    if obj in mem:
        return mem[obj]

    total = 1
    for other in orbits[obj]:
        total += num_orbits(other, orbits, mem)

    mem[obj] = total
    return total


def compute(cts: str) -> int:
    pairs = cts.strip().splitlines()

    orbits = defaultdict(set)
    for pair in pairs:
        left, right = pair.split(')')
        orbits[right].add(left)

    mem: Dict[str, int] = {}
    total = 0
    for obj in orbits.keys():
        total += num_orbits(obj, orbits, mem)

    return total


@pytest.mark.parametrize(
    'input_str, expected', [
        ('COM)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L', 42)
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
