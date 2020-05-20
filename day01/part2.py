#!/usr/bin/env python3
import pytest


def fuel_for_mass(mass: int) -> int:
    fuel = max(mass // 3 - 2, 0)
    return fuel + (fuel_for_mass(fuel) if fuel > 0 else 0)


def compute(cts: str) -> int:
    total = 0
    for line in cts.splitlines():
        line_val = int(line)
        total += fuel_for_mass(line_val)
    return total


@pytest.mark.parametrize(
    'input_str, expected', [
        ('14', 2),
        ('1969', 966),
        ('100756', 50346),
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
