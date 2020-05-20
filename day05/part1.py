#!/usr/bin/env python3
import pytest

from typing import List, Dict, Callable, Tuple

Program = List[int]


class Intcode:
    def __init__(self, mem: Program, debug_enabled: bool = False):
        self.debug_enabled = debug_enabled
        self.pc = 0
        self.mem = mem[:]
        self.num_input_commands = 0

    def run_program(self) -> Program:
        OPCODES: Dict[int, Tuple[Callable[..., None], int]] = {
            1: (self.do_add, 2),
            2: (self.do_mul, 2),
            3: (self.do_input, 0),
            4: (self.do_output, 1),
        }

        while self.mem[self.pc] != 99:
            opcode = self.mem[self.pc]
            param_types, opcode = opcode // 100, opcode % 100

            fn, num_args = OPCODES[opcode]

            args = self.mem[self.pc + 1:self.pc + 1 + num_args][:]
            for i, arg in enumerate(args):
                if param_types % 10 == 0:
                    args[i] = self.mem[arg]
                param_types //= 10

            assert opcode >= 0
            self.debug('opcode', opcode, 'at', self.pc, 'has param_types', param_types)
            fn(*args)

        return self.mem

    def do_add(self, a: int, b: int) -> None:
        c = self.mem[self.pc + 3]
        self.debug('mem', c, '=', a, '+', b)
        self.mem[c] = a + b
        self.pc += 4

    def do_mul(self, a: int, b: int) -> None:
        c = self.mem[self.pc + 3]
        self.debug('mem', c, '=', a, '*', b)
        self.mem[c] = a * b
        self.pc += 4

    def do_input(self) -> None:
        assert self.num_input_commands == 0
        self.num_input_commands += 1

        a = self.mem[self.pc + 1]
        self.mem[a] = 1
        self.debug('mem', a, '= 1')
        self.pc += 2

    def do_output(self, a: int) -> None:
        print('OUTPUT:', a)
        self.pc += 2

    def debug(self, *args) -> None:
        if self.debug_enabled:
            print(*args)


def run_program(mem: Program) -> Program:
    intcode = Intcode(mem)
    return intcode.run_program()


def compute(cts: str) -> Program:
    mem = list(map(int, cts.strip().split(',')))
    return run_program(mem)


@pytest.mark.parametrize(
    'input_list, expected', [
        ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
        ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
        ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
        ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ]
)
def test_compute(input_list: Program, expected: Program) -> None:
    assert run_program(input_list) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print()
    compute(cts)

    return 0


if __name__ == '__main__':
    exit(main())
