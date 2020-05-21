#!/usr/bin/env python3
import pytest
from itertools import cycle
from typing import List, Iterator


def get_pattern_for(i: int) -> Iterator[int]:
    m = i + 1
    pattern = ([0] * m) + ([1] * m) + ([0] * m) + ([-1] * m)
    return cycle(pattern[1:] + pattern[:1])


def fft(digits: List[int]):
    output = []
    for i, digit in enumerate(digits):
        patterns = get_pattern_for(i)
        res = 0
        for digit2 in digits:
            pattern = next(patterns)
            res += digit2 * pattern
        output.append(abs(res) % 10)
    return output


def compute(cts: str, num_iterations: int) -> str:
    digits = list(map(int, cts))
    for i in range(num_iterations):
        digits = fft(digits)
    return ''.join(map(str, digits[:8]))


@pytest.mark.parametrize(
    'input_str, num_iterations, expected', [
        ('12345678', 4, '01029498'),
        ('80871224585914546619083218645595', 100, '24176176'),
        ('19617804207202209144916044189917', 100, '73745418'),
        ('69317163492948606335995924319873', 100, '52432133'),
    ]
)
def test_compute(input_str: str, num_iterations: int, expected: str):
    assert compute(input_str, num_iterations) == expected


def main():
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts, 100))

    return 0


if __name__ == '__main__':
    exit(main())
