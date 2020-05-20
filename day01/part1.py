#!/usr/bin/env python3
import pytest


def compute(cts: str) -> int:
    return sum(int(line) // 3 - 2 for line in cts.splitlines())


@pytest.mark.parametrize(
    'input_str, expected', [
        ('12', 2),
        ('14', 2),
        ('1969', 654),
        ('100756', 33583),
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
