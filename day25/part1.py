#!/usr/bin/env python3
from itertools import combinations
from typing import List, Iterator, Generator, Dict, Callable, Tuple, Optional, Set

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
                yield None
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


MOVES = {
    'N': 'north',
    'E': 'east',
    'S': 'south',
    'W': 'west',
}

MOVES_REV = {
    'N': 'south',
    'E': 'west',
    'S': 'north',
    'W': 'east',
}


NON_DESIRABLE_ITEMS = [
    'photons',
    'escape pod',
    'molten lava',
    'infinite loop',
    'giant electromagnet',
]


class Strategy:
    def __init__(self, droid):
        self.droid = droid

    def get_inputs(self) -> Generator[int, None, None]:
        raise NotImplementedError()

    def on_output(self) -> None:
        droid = self.droid
        print(droid.screen)


class CollectionStrategy(Strategy):
    def get_inputs(self) -> Generator[int, None, None]:
        droid = self.droid

        if droid.items_here:
            yield from droid.take_items(droid.items_here)
            droid.inventory.extend(droid.items_here)
            droid.items_here = []
        else:
            goto = droid.open.pop()
            # print('going to:', goto, 'at', droid.moves)
            yield from droid.move_to(goto)

    def parse_screen(self) -> Tuple[str, List[str], List[str]]:
        droid = self.droid

        title = ''
        doors = []
        items = []
        list_type = None

        for line in droid.screen.splitlines():
            if line.startswith('=='):
                title = line[3:-3]
            elif line == 'Doors here lead:':
                list_type = 'doors'
            elif line == 'Items here:':
                list_type = 'items'
            elif line.startswith('- '):
                if list_type == 'doors':
                    doors.append(line[2:][0].upper())
                else:
                    assert list_type == 'items'
                    items.append(line[2:])

        return title, doors, items

    def on_output(self) -> None:
        super().on_output()
        droid = self.droid

        title, doors, items = self.parse_screen()

        droid.visited.add(droid.moves)

        if title == 'Security Checkpoint':
            droid.security_checkpoint = droid.moves
            return

        for item in items:
            if item not in NON_DESIRABLE_ITEMS:
                droid.items_here.append(item)

        for door in doors:
            door_moves = droid.moves + door
            if door_moves in droid.visited or door_moves in droid.open:
                continue
            if door_moves[-2:] in ['EW', 'WE', 'SN', 'NS']:
                continue
            droid.open.append(door_moves)

        if not droid.open:
            droid.strategy = GotoSecCheckStrategy(droid)
            print('CHANGING STRATEGY TO', droid.strategy)


class GotoSecCheckStrategy(Strategy):
    def get_inputs(self) -> Generator[int, None, None]:
        droid = self.droid

        yield from droid.move_to(droid.security_checkpoint)
        yield from droid.drop_items(droid.inventory)
        droid.strategy = PermutateInventoryStrategy(droid)


class PermutateInventoryStrategy(Strategy):
    def get_inputs(self) -> Generator[int, None, None]:
        droid = self.droid

        for i in range(1, len(droid.inventory) + 1):
            combs = combinations(droid.inventory, i)
            for items in combs:
                yield from droid.take_items(items)
                yield from (ord(c) for c in 'south\n')
                yield from droid.drop_items(items)


class Droid:
    moves: str
    open: List[str]
    visited: Set[str]
    security_checkpoint: Optional[str]
    items_here: List[str]
    inventory: List[str]
    strategy: Strategy

    def __init__(self, prog: Program):
        self.intc = Intcode(prog, self.get_inputs())

        self.moves = ''
        self.open = []
        self.visited = set()
        self.security_checkpoint = None

        self.items_here = []
        self.inventory = []

        self.strategy = CollectionStrategy(self)

    def take_items(self, items: List[str]) -> Generator[int, None, None]:
        for item in items:
            for c in 'take {}\n'.format(item):
                yield ord(c)

    def drop_items(self, items: List[str]) -> Generator[int, None, None]:
        for item in items:
            for c in 'drop {}\n'.format(item):
                yield ord(c)

    def move_to(self, goto: str) -> Generator[int, None, None]:
        for i in range(len(goto)):
            if i == len(self.moves):
                break
            if self.moves[i] != goto[i]:
                break

        backtrack = self.moves[i:][::-1]
        for move in backtrack:
            print('- backtrack:', MOVES_REV[move])
            self.moves = self.moves[:-1]
            for c in MOVES_REV[move] + '\n':
                yield ord(c)

        for move in goto[i:]:
            self.moves = self.moves + move
            print('- walking:', MOVES[move])
            for c in MOVES[move] + '\n':
                yield ord(c)

    def get_inputs(self) -> Generator[int, None, None]:
        while True:
            yield from self.strategy.get_inputs()

    def fetch_screen(self) -> bool:
        self.screen = ''

        for o in self.intc.iterable():
            if o is None:
                return True
            assert 10 <= o < 128
            self.screen += chr(o)

            if self.screen.endswith('Command?\n'):
                break

        self.screen = self.screen.strip()
        return False

    def run(self) -> None:
        while True:
            halted = self.fetch_screen()
            if halted:
                print(self.screen)
                break

            if 'You take' in self.screen:
                continue

            self.strategy.on_output()


def compute(cts: str) -> None:
    prog = str_to_prog(cts)
    droid = Droid(prog)
    droid.run()


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    compute(cts)

    return 0


if __name__ == '__main__':
    exit(main())
