#!/usr/bin/env python3
import pytest


def compute(cts: str):
    raise NotImplementedError


@pytest.mark.parametrize(
    'input_str, expected', [
    ]
)
def test_compute(input_str, expected) -> None:
    assert compute(input_str) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
