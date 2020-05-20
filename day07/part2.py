#!/usr/bin/env python
from itertools import permutations, cycle

import pytest

from typing import List, Dict, Callable, Iterator, Generator

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
        for _ in self.run_until_output():
            pass

    def feed(self, inputs):
        self.inputs = inputs
        for output in self.run_until_output():
            return output

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
        }

        while True:
            opc = self.get_param(output=True)
            opc, self.param_spec = opc % 100, opc // 100
            if opc == 99:
                break

            fn = OPCODES[opc]
            fn()
            if opc == 4:
                yield self.output

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


def compute_once(prog: Program, inputs: List[int]) -> int:
    ints = [Intcode(prog, iter([i])) for i in inputs]

    last_output = 0
    for i, intc in enumerate(ints):
        last_output = intc.feed(iter([inputs[i], last_output]))

    for intc in cycle(ints):
        output = intc.feed(iter([last_output]))
        if output is None:
            break
        last_output = output

    return last_output


def compute_best(cts: str):
    prog = list(map(int, cts.split(',')))
    best = 0
    for a, b, c, d, e in permutations([5, 6, 7, 8, 9]):
        output = compute_once(prog, [a, b, c, d, e])
        print(a, b, c, d, e, 'OUTPUT', output)
        best = max(output, best)
    return best


@pytest.mark.parametrize(
    'inp, exp', [
        ('3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5',
            139629729),
        ('3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,'
         '1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10',
            18216),
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
