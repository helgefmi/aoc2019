#!/usr/bin/env python
from textwrap import wrap


def compute(cts, rows, cols):
    layer_size = rows * cols

    layers = wrap(cts, layer_size)
    layers = [map(int, layer) for layer in layers]

    output = [2] * layer_size
    for layer in layers:
        for i, pixel in enumerate(layer):
            if pixel < 2 and output[i] == 2:
                output[i] = pixel

    output_str = ''.join('.' if pixel == 0 else 'X' for pixel in output)
    for line in wrap(output_str, cols):
        print(line)


def main() -> int:
    with open('day08.txt') as f:
        cts = f.read()

    print(compute(cts, 6, 25))

    return 0


if __name__ == '__main__':
    exit(main())
