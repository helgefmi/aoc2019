#!/usr/bin/env python
from itertools import islice
from typing import List, Dict, Callable, Iterator, Generator, Tuple

Program = List[int]


def take(n, iterable):
    return list(islice(iterable, n))


def str_to_prog(s: str) -> List[int]:
    return list(map(int, s.strip().split(',')))


class Intcode:
    def __init__(self, prog: Program, inputs: Iterator[int]):
        self.prog = prog[:] + [0] * (1024 * 1024 - len(prog))
        self.pc = 0
        self.inputs = inputs
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

    def run(self) -> List[int]:
        ret = []
        for output in self.run_until_output():
            ret.append(output)
        return ret

    def feed(self, inputs, num_outputs):
        self.inputs = iter(inputs)
        return list(take(num_outputs, self.run_until_output()))

    def run_until_output(self) -> Generator[int, int, None]:
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


def update_coord(coord, direction, face):
    L = [(1, 0), (0, 1), (-1, 0), (0, -1)] * 3
    i = L.index(direction, 1)
    return L[i + (-1 if face == 0 else 1)]


def compute(cts: str) -> int:
    prog = str_to_prog(cts)

    area: Dict[Tuple[int, int], int] = {}
    coord = (0, 0)
    direction = (1, 0)

    intc = Intcode(prog, iter([]))

    while True:
        print(coord, end=' ')
        output = intc.feed([area.get(coord, 0)], 2)
        if not output:
            print('done')
            break

        color, face = output
        print(color, face)

        area[coord] = color
        direction = update_coord(coord, direction, face)
        coord = (coord[0] + direction[0], coord[1] + direction[1])

    return len(area.keys())


def main() -> int:
    with open('day11.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
