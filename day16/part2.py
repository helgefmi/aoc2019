#!/usr/bin/env python3
import pytest

import numpy as np


def fft(arr: np.array, arr_len: int, from_i: int):
    acc = 0
    for i in reversed(range(arr_len)):
        acc += arr[i]
        arr[i] = abs(acc) % 10


def compute(cts: str, num_iterations: int) -> str:
    from_i = int(cts[:7])
    cts = (cts * 10000)[from_i:]

    arr = np.array(list(map(int, cts)), dtype=int)
    arr_len = len(arr)

    for i in range(num_iterations):
        print('iteration', i)
        fft(arr, arr_len, 0)

    return ''.join(map(str, arr[:8]))


@pytest.mark.parametrize(
    'input_str, num_iterations, expected', [
        ('03036732577212944063491565474664', 100, '84462026'),
        ('02935109699940807407585447034323', 100, '78725270'),
        ('03081770884921959731165446850517', 100, '53553731'),
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
