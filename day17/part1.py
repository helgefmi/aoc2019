#!/usr/bin/env python3
from typing import List, Iterator, Callable, Generator, Dict, Tuple

Program = List[int]
Coord = Tuple[int, int]


def str_to_prog(s: str) -> List[int]:
    return list(map(int, s.strip().split(',')))


class Intcode:
    def __init__(self, prog: Program, inputs: Iterator[int] = iter([])):
        self.prog = prog[:] + [0] * (1024 * 1024 - len(prog))
        self.pc = 0
        self.inputs = iter(inputs)
        self.output = 0
        self.param_spec = 0
        self.rel_base = 0

    def get_param(self, is_write: bool = False) -> int:
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

    def op_add(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a + b

    def op_multiply(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = a * b

    def op_input(self) -> None:
        a = self.get_param(is_write=True)
        self.prog[a] = next(self.inputs)

    def op_output(self) -> None:
        self.output = self.get_param()

    def op_jump_if_true(self) -> None:
        a = self.get_param()
        b = self.get_param()
        if a:
            self.pc = b

    def op_jump_if_false(self) -> None:
        a = self.get_param()
        b = self.get_param()
        if not a:
            self.pc = b

    def op_less_than(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a < b else 0

    def op_equals(self) -> None:
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(is_write=True)
        self.prog[c] = 1 if a == b else 0

    def op_rel_base(self) -> None:
        a = self.get_param()
        self.rel_base += a


def find_intersections(area: List[str]) -> Generator[Coord, None, None]:
    for y in range(1, len(area) - 2):
        for x in range(1, len(area[0]) - 1):
            if area[y][x - 1:x + 2] == '###':
                if area[y - 1][x + 1] == area[y + 1][x + 1] == '#':
                    yield (y, x + 1)


def sum_intersections(area_str: str) -> int:
    print(area_str)

    area = area_str.splitlines()
    acc = 0
    for y, x in find_intersections(area):
        acc += y * x
    return acc


def compute(cts: str) -> int:
    prog = str_to_prog(cts)
    intc = Intcode(prog)

    area_str = ''
    for i in intc.iterable():
        area_str += chr(i)

    return sum_intersections(area_str)


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
