#!/usr/bin/env python3
from collections import deque
from itertools import islice
from typing import List, Iterator, Generator, Dict, Callable, Tuple, Optional

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

    def feed(self, inputs):
        self.inputs = iter(inputs)
        for o in self.iterable():
            return o

    def has_output(self):
        for o in self.iterable():
            return 0

    def iterable(self) -> Generator[Optional[int], None, None]:
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
            elif opc == 3:
                yield None

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


class NIC:
    intc: Intcode
    net_addr: int
    queue: deque

    def __init__(self, prog: Program, net_addr: int):
        self.intc = Intcode(prog, self.get_inputs())
        self.net_addr = net_addr
        self.queue = deque()

    def add_packet(self, x: int, y: int) -> None:
        self.queue.append((x, y))

    def get_inputs(self) -> Generator[int, None, None]:
        yield self.net_addr

        while True:
            if not self.queue:
                yield -1
            else:
                x, y = self.queue.popleft()
                yield x
                yield y

    def read(self, timeout: int) -> Optional[int]:
        while timeout:
            output = next(self.intc.iterable())
            if output is not None:
                return output
            timeout -= 1
        return None


def compute(cts: str) -> int:
    prog = str_to_prog(cts)

    network = [NIC(prog, i) for i in range(50)]
    nat_packet = (-1, -1)
    last_nat_packet = None
    while True:
        all_idle = True

        for nic in network:
            if nic.queue:
                all_idle = False

            while True:
                output = nic.read(5)
                if output is None:
                    break

                all_idle = False

                dest = output
                x, y = islice(nic.intc.iterable(), 0, 2)
                assert x is not None and y is not None

                if dest == 255:
                    nat_packet = (x, y)
                else:
                    network[dest].add_packet(x, y)

        if all_idle:
            if nat_packet == last_nat_packet:
                return nat_packet[1]
            network[0].add_packet(*nat_packet)
            last_nat_packet = nat_packet


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
