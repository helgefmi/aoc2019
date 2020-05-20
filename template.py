#!/usr/bin/env python3
import pytest


def compute(cts):
    raise NotImplementedError


@pytest.mark.parametrize(
    'input_str, expected', [
    ]
)
def test_compute(input_str, expected):
    assert compute(input_str) == expected


def main():
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
