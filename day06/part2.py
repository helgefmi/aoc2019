#!/usr/bin/env python3
from collections import defaultdict

from typing import Dict, Set

import pytest


def num_transitions(obj: str, end: str, orbits: Dict[str, Set[str]]) -> int:
    if obj == end:
        return 0

    best = 10**6
    for other in orbits[obj]:
        orbits[other].remove(obj)
        best = min(best, 1 + num_transitions(other, end, orbits))

    # mem[obj] = best
    return best


def compute(cts: str) -> int:
    pairs = cts.strip().splitlines()

    orbits = defaultdict(set)
    for pair in pairs:
        left, right = pair.split(')')
        orbits[right].add(left)
        orbits[left].add(right)

    return num_transitions(next(iter(orbits['YOU'])), next(iter(orbits['SAN'])), orbits)


@pytest.mark.parametrize(
    'input_str, expected', [
        ('COM)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L\nK)YOU\nI)SAN', 4),
        ('COM)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L\nK)K2\nK2)YOU\nI)SAN', 5),
        ('COM)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L\nK)K2\nK2)YOU\nI)I2\nI2)SAN', 6),
        ('SAN)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L\nK)YOU\nI)COM', 5),
        ('SAN)B\nB)C\nC)D\nD)E\nE)F\nB)G\nG)H\nD)I\nE)J\nJ)K\nK)L\nK)COM\nI)YOU', 3),
    ]
)
def test_compute(input_str: str, expected: int) -> None:
    assert compute(input_str) == expected
    rev_str = input_str.replace('SAN', '|').replace('YOU', 'SAN').replace('|', 'YOU')
    assert compute(rev_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
