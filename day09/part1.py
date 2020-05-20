#!/usr/bin/env python
from typing import List, Dict, Callable, Iterator, Generator

Program = List[int]


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

    def get_param(self, output=False):
        ret = self.prog[self.pc]
        self.pc += 1

        addr_mode = self.param_spec % 10
        self.param_spec //= 10

        if not output:
            if addr_mode == 0:
                ret = self.prog[ret]
            elif addr_mode == 2:
                ret = self.prog[self.rel_base + ret]
        else:
            if addr_mode == 2:
                ret = ret + self.rel_base
        return ret

    def run(self) -> List[int]:
        ret = []
        for output in self.run_until_output():
            ret.append(output)
        return ret

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
            9: self.op_rel_base,
        }

        while True:
            opc = self.prog[self.pc]
            self.pc += 1

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

    def op_rel_base(self):
        a = self.get_param()
        self.rel_base += a


def compute(cts: str, inputs) -> List[int]:
    prog = str_to_prog(cts)
    intc = Intcode(prog, iter(inputs))
    return list(intc.run())


def test_produce_copy() -> None:
    prog_str = '109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99'
    output = compute(prog_str, [])
    assert output == str_to_prog(prog_str)


def test_output_16_digit_number() -> None:
    prog_str = '1102,34915192,34915192,7,4,7,99,0'
    output = compute(prog_str, [])
    assert len(output) == 1 and len(str(output[0])) == 16


def test_should_output_large_number() -> None:
    prog_str = '104,1125899906842624,99'
    output = compute(prog_str, [])
    assert len(output) == 1 and output[0] == 1125899906842624


def main() -> int:
    with open('day9.txt', 'r') as f:
        cts = f.read()

    print(compute(cts, [1]))

    return 0


if __name__ == '__main__':
    exit(main())
