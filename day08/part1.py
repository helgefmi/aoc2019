#!/usr/bin/env python
from collections import Counter
from textwrap import wrap


def compute(cts, rows, cols):
    layers = wrap(cts, rows * cols)
    counters = [Counter(layer) for layer in layers]

    layer = sorted(counters, key=lambda c: c['0'])[0]

    return layer['1'] * layer['2']


def main() -> int:
    with open('day08.txt') as f:
        cts = f.read()

    print(compute(cts, 6, 25))

    return 0


if __name__ == '__main__':
    exit(main())
