#!/usr/bin/env python3
from enum import Enum
from itertools import islice
from typing import List, Dict, Callable, Iterator, Generator

Program = List[int]

WIDTH = 80
HEIGHT = 24


class Tile(Enum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    HOR_PADDLE = 3
    BALL = 4

    def to_char(self):
        chars = {
            Tile.EMPTY: ' ',
            Tile.WALL: '#',
            Tile.BLOCK: '¤',
            Tile.HOR_PADDLE: '-',
            Tile.BALL: '*',
        }
        return chars[self]


def take(iterable, n):
    return list(islice(iterable, n))


def takeby(iterable: Iterator[int], n: int):
    while True:
        tup = tuple(take(iterable, n))
        if not tup:
            return
        yield tup


def str_to_prog(s: str) -> List[int]:
    return list(map(int, s.strip().split(',')))


class Intcode:
    def __init__(self, prog: Program, inputs: List[int] = []):
        self.prog = prog[:] + [0] * (1024 * 1024 - len(prog))
        self.pc = 0
        self.inputs = iter(inputs)
        self.output = 0
        self.param_spec = 0
        self.rel_base = 0

    def get_param(self, is_write=False):
        ret = self.prog[self.pc]
        self.pc += 1

        addr_mode = self.param_spec % 10
        self.param_spec //= 10

        if not is_write:
            if addr_mode == 0:
                ret = self.prog[ret]
            elif addr_mode == 2:
                ret = self.prog[self.rel_base + ret]
        elif addr_mode == 2:
            ret = ret + self.rel_base

        return ret

    def iterable(self) -> Generator[int, int, None]:
        OPCODES: Dict[int, Callable[..., None]] = {
            1: self.op_add,
            2: self.op_multiply,
            3: self.op_input,
            4: self.op_output,
            5: self.op_jump_if_true,
            6: self.op_jump_if_false,
            7: self.op_less_than,
            8: self.op_equals,
            9: self.op_rel_base,
        }

        while True:
            opc = self.prog[self.pc]
            self.pc += 1

            opc, self.param_spec = opc % 100, opc // 100
            if opc == 99:
                print('halt')
                break

            fn = OPCODES[opc]

            fn()
            if opc == 4:
                yield self.output

    def op_add(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a + b

    def op_multiply(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a * b

    def op_input(self):
        a = self.get_param(is_write=True)
        self.prog[a] = next(self.inputs)

    def op_output(self):
        self.output = self.get_param()

    def op_jump_if_true(self):
        a = self.get_param()
        b = self.get_param()
        if a:
            self.pc = b

    def op_jump_if_false(self):
        a = self.get_param()
        b = self.get_param()
        if not a:
            self.pc = b

    def op_less_than(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a < b else 0

    def op_equals(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a == b else 0

    def op_rel_base(self):
        a = self.get_param()
        self.rel_base += a


def print_screen(screen):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            print(screen[y][x].to_char(), end='')
        print()


def compute(cts: str) -> int:
    prog = str_to_prog(cts)
    intc = Intcode(prog)

    screen = [[Tile.EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for x, y, tile_id in takeby(intc.iterable(), 3):
        screen[y][x] = Tile(tile_id)

    return sum(sum(1 for tile in row if tile == Tile.BLOCK) for row in screen)


def main() -> int:
    with open('day13.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
