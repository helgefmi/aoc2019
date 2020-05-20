#!/usr/bin/env python3
import pytest

from typing import List, Optional, Dict, Callable, Tuple

Program = List[int]


class Intcode:
    def __init__(self, mem: Program, input_val: int, debug_enabled: bool = False):
        self.debug_enabled = debug_enabled
        self.pc = 0
        self.mem = mem[:]
        self.input_val = input_val
        self.num_input_commands = 0
        self.param_types = 0

    def get_opcode(self) -> int:
        opcode = self.mem[self.pc]
        self.pc += 1
        return opcode

    def get_param(self) -> int:
        param = self.mem[self.pc]
        if self.param_types % 10 == 0:
            param = self.mem[param]
        self.param_types //= 10
        self.pc += 1
        return param

    def get_write_param(self) -> int:
        ret = self.mem[self.pc]
        self.pc += 1
        return ret

    def set_memory(self, value: int) -> None:
        self.mem[self.pc] = value
        self.pc += 1

    def run_program(self) -> Optional[int]:
        OPCODES: Dict[int, Tuple[Callable[..., Optional[int]], int, int]] = {
            1: (self.do_add, 2, 1),
            2: (self.do_mul, 2, 1),
            3: (self.do_input, 0, 1),
            4: (self.do_output, 1, 0),
            5: (self.jmp_if_true, 2, 0),
            6: (self.jmp_if_false, 2, 0),
            7: (self.lt, 2, 1),
            8: (self.eq, 2, 1),
        }

        output: Optional[int] = None
        while True:
            opcode = self.get_opcode()
            self.debug('opcode', opcode, ', pc =', self.pc)

            if opcode == 99:
                break

            self.param_types, opcode = opcode // 100, opcode % 100

            fn, num_params, num_write_params = OPCODES[opcode]
            args = [self.get_param() for _ in range(num_params)]
            args += [self.get_write_param() for _ in range(num_write_params)]

            self.debug('- fn:', fn.__name__)
            self.debug('- args:', args)
            output = fn(*args)

        return output

    def do_add(self, a: int, b: int, c: int) -> None:
        self.debug('! mem', c, '=', a, '+', b)
        self.mem[c] = a + b

    def do_mul(self, a: int, b: int, c: int) -> None:
        self.debug('! mem', c, '=', a, '*', b)
        self.mem[c] = a * b

    def do_input(self, a: int) -> None:
        assert self.num_input_commands == 0
        self.num_input_commands += 1

        self.mem[a] = self.input_val
        self.debug('! mem', a, '=', self.input_val)

    def jmp_if_true(self, a: int, b: int) -> None:
        self.pc = b if a else self.pc
        self.debug('!pc =', self.pc)

    def jmp_if_false(self, a: int, b: int) -> None:
        self.pc = b if not a else self.pc
        self.debug('!pc =', self.pc)

    def do_output(self, a: int) -> int:
        print('OUTPUT:', a)
        return a

    def lt(self, a: int, b: int, c: int) -> None:
        self.mem[c] = 1 if a < b else 0
        self.debug('! mem', c, '=', self.mem[c])

    def eq(self, a: int, b: int, c: int) -> None:
        self.mem[c] = 1 if a == b else 0
        self.debug('! mem', c, '=', self.mem[c])

    def debug(self, *args) -> None:
        if self.debug_enabled:
            print(*args)


def run_program(program: Program, input_val: int):
    intcode = Intcode(program, input_val)
    return intcode.run_program()


def compute(cts: str, input_val: int):
    mem = list(map(int, cts.strip().split(',')))
    return run_program(mem, input_val)


@pytest.mark.parametrize(
    'program, input_val, expected', [
        ([3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, -1, 0, 1, 9], 0, 0),
        ([3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1], 0, 0),
        ([3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, -1, 0, 1, 9], 1, 1),
        ([3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1], 1, 1),
        ([3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, -1, 0, 1, 9], -52, 1),
        ([3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1], 99, 1),
    ]
)
def test_compute(program: Program, input_val: int, expected: int) -> None:
    assert run_program(program, input_val) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print()
    print('computed:', compute(cts, 5))

    return 0


if __name__ == '__main__':
    exit(main())
