#!/usr/bin/env python3
import pytest

from typing import List, Dict, Callable, Optional


OPCODES: Dict[int, Callable[[int, int], int]] = {
    1: lambda a, b: a + b,
    2: lambda a, b: a * b,
}


def run_program(mem: List[int]) -> List[int]:
    mem = mem[:]
    pc = 0
    while mem[pc] != 99:
        opcode, pos_a, pos_b, pos_c = mem[pc:pc + 4]
        mem[pos_c] = OPCODES[opcode](mem[pos_a], mem[pos_b])
        pc += 4
    return mem


def compute(cts: str) -> Optional[int]:
    mem = list(map(int, cts.strip().split(',')))
    for a in range(100):
        for b in range(100):
            mem[1] = a
            mem[2] = b
            if run_program(mem)[0] == 19690720:
                return 100 * a + b
    return None


@pytest.mark.parametrize(
    'input_list, expected', [
        ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
        ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
        ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
        ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ]
)
def test_compute(input_list: List[int], expected: List[int]) -> None:
    assert run_program(input_list) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
