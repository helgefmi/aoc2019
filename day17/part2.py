#!/usr/bin/env python3
from typing import List, Iterator, Callable, Generator, Dict, Tuple
from itertools import count

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


def char_to_direction(c: str) -> Coord:
    return {
        '^': (0, -1),
        '>': (1, 0),
        'v': (0, 1),
        '<': (-1, 0),
    }[c]


def get_dir_str(old_dir: Coord, new_dir: Coord) -> str:
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)] * 2
    old_i = dirs.index(old_dir, 1)
    new_i = dirs.index(new_dir, old_i - 1)

    assert abs(new_i - old_i) == 1
    return 'L' if new_i < old_i else 'R'


class Robot:
    prog: Program
    area: List[str]

    def __init__(self, prog: Program):
        self.prog = prog
        self.area = []

    def calculate_sequence(self) -> List[str]:
        area = [list(row) for row in self.area]

        height, width = len(area), len(area[0])

        def valid_coordinate(x, y):
            return 0 <= x < width and 0 <= y < height

        for y, row in enumerate(area):
            for x, c in enumerate(row):
                if c in '^>v<':
                    rob_x = x
                    rob_y = y
                    cur_dir = char_to_direction(c)

        seq = []
        while any(tile == '#' for row in area for tile in row):
            avail_dirs = []
            for x, y in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                new_x = rob_x + x
                new_y = rob_y + y
                if not valid_coordinate(new_x, new_y):
                    continue
                if area[new_y][new_x] == '#':
                    avail_dirs.append((x, y))

            assert len(avail_dirs) == 1

            new_dir = avail_dirs.pop()
            seq.append(get_dir_str(cur_dir, new_dir))
            cur_dir = new_dir

            for n in count(1):
                new_x = rob_x + new_dir[0]
                new_y = rob_y + new_dir[1]

                if not valid_coordinate(new_x, new_y):
                    break

                if area[new_y][new_x] not in '*#':
                    break

                rob_x = new_x
                rob_y = new_y
                area[rob_y][rob_x] = '*'

            seq.append(str(n - 1))

        return seq

    def optimize_sequence(self, seq: List[str]) -> str:
        possible_seqs = []
        for i in range(len(seq)):
            for i2 in range(i, len(seq)):
                possible_seq_str = ','.join(seq[i:i2])
                if len(possible_seq_str) > 20:
                    break
                possible_seqs.append(possible_seq_str)

        seq_str = ','.join(seq)
        for i, a in enumerate(possible_seqs):
            a_str = seq_str.replace(a, 'A')
            for i2, b in enumerate(possible_seqs[i + 1:]):
                b_str = a_str.replace(b, 'B')
                for i3, c in enumerate(possible_seqs[i2 + 1:]):
                    c_str = b_str.replace(c, 'C')
                    if all(x in 'ABC,' for x in c_str):
                        return '\n'.join([c_str, a, b, c])

        raise RuntimeError('no optimal sequence found')

    def get_inputs(self) -> Generator[int, None, None]:
        full_seq = self.calculate_sequence()
        full_seq_str = self.optimize_sequence(full_seq)
        full_seq_str += '\nn\n'

        for c in full_seq_str:
            yield ord(c)

    def fetch_area(self) -> None:
        intc = Intcode(self.prog)
        area = ''
        for i in intc.iterable():
            area += chr(i)
        self.area = area.strip().splitlines()

    def run(self) -> int:
        self.fetch_area()

        prog = self.prog[:]
        prog[0] = 2
        intc = Intcode(prog, self.get_inputs())
        for i in intc.iterable():
            if i <= 128:
                print(chr(i), end='')
            else:
                return i

        raise RuntimeError('unreachable')


def compute(cts: str) -> int:
    prog = str_to_prog(cts)
    robot = Robot(prog)
    return robot.run()


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
