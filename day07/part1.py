#!/usr/bin/env python
from itertools import permutations

import pytest

from typing import List, Dict, Callable, Iterator

Program = List[int]


class Intcode:
    def __init__(self, prog: Program, inputs: Iterator[int]):
        self.prog = prog[:]
        self.pc = 0
        self.inputs = inputs
        self.output = 0
        self.param_spec = 0

    def get_param(self, output=False):
        ret = self.prog[self.pc]
        self.pc += 1
        if not output:
            if self.param_spec % 10 == 0:
                ret = self.prog[ret]
            self.param_spec //= 10
        return ret

    def run(self) -> None:
        OPCODES: Dict[int, Callable[..., None]] = {
            1: self.op_add,
            2: self.op_multiply,
            3: self.op_input,
            4: self.op_output,
            5: self.op_jump_if_true,
            6: self.op_jump_if_false,
            7: self.op_less_than,
            8: self.op_equals,
        }

        while True:
            opc = self.get_param(output=True)
            opc, self.param_spec = opc % 100, opc // 100
            if opc == 99:
                break

            fn = OPCODES[opc]
            fn()

    def op_add(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(output=True)
        self.prog[c] = a + b

    def op_multiply(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(output=True)
        self.prog[c] = a * b

    def op_input(self):
        a = self.get_param(output=True)
        self.prog[a] = next(self.inputs)

    def op_output(self):
        self.output = self.get_param()
        # print('OUTPUT:', self.output)

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
        c = self.get_param(output=True)
        self.prog[c] = 1 if a < b else 0

    def op_equals(self):
        a = self.get_param()
        b = self.get_param()
        c = self.get_param(output=True)
        self.prog[c] = 1 if a == b else 0


def compute_once(prog: Program, inputs: Iterator[int]) -> int:
    last_output = 0
    for _ in range(5):
        intc = Intcode(prog, iter([next(inputs), last_output]))
        intc.run()
        last_output = intc.output
    return last_output


def compute_best(cts: str):
    prog = list(map(int, cts.split(',')))
    best = 0
    for a, b, c, d, e in permutations([0, 1, 2, 3, 4]):
        output = compute_once(prog, iter([a, b, c, d, e]))
        print(a, b, c, d, e, 'OUTPUT', output)
        best = max(output, best)
    return best


@pytest.mark.parametrize(
    'inp, exp', [
        ('3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0', 43210),
        ('3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0', 54321),
        ('3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0', 65210),
    ]
)
def test_run_once(inp: str, exp: int) -> None:
    assert compute_best(inp) == exp


def main() -> int:
    with open('day7.txt', 'r') as f:
        cts = f.read()

    print(compute_best(cts))

    return 0


if __name__ == '__main__':
    exit(main())
