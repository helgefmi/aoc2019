#!/usr/bin/env python

# Thanks to https://github.com/sophiebits/adventofcode/blob/master/2019/day14.py.
# Read through the code, and made another attempt, since my initial solution was
# so horribly slow (25 min, one fuel at a time.)

import pytest

TARGET = 1000000000000


def parse_chemical(s):
    num, name = s.split(' ')
    return name, int(num)


def input_to_rules(cts):
    ret = {}
    for line in cts.splitlines():
        left, right = line.split(' => ')

        lefts = list(map(parse_chemical, left.split(', ')))
        to_name, to_num = parse_chemical(right)

        ret[to_name] = {
            'makes': to_num,
            'children': dict(lefts),
        }
    return ret


def ore_for_fuel(rules, test_fuel):
    have = {}
    need = {'FUEL': test_fuel}

    while not all(x == 'ORE' for x in need):
        need_name, need_value = [(k, v) for k, v in need.items() if k != 'ORE'][0]
        need_data = rules[need_name]

        d, m = divmod(need_value, need_data['makes'])
        need.pop(need_name)

        if m:
            # We still need it if there's a remainder, so instead, "buy" another one and put the rest in `have`.
            have[need_name] = m
            d += 1

        for other_name, other_value in need_data['children'].items():
            need[other_name] = other_value * d + need.get(other_name, 0) - have.get(other_name, 0)

    return need['ORE']


def compute(cts):
    rules = input_to_rules(cts)

    test_max = 1
    while ore_for_fuel(rules, test_max) < TARGET:
        test_max *= 10

    test_min = test_max // 10

    while test_min < test_max:
        pivot = (test_min + test_max) // 2
        result = ore_for_fuel(rules, pivot)

        if result < TARGET:
            test_min = pivot + 1
        elif result > TARGET:
            test_max = pivot - 1
        else:
            return pivot
    return test_min


INPUT_3 = """
157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT
""".strip()

INPUT_4 = """
2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF
""".strip()

INPUT_5 = """
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX
""".strip()


@pytest.mark.parametrize(
    'input_s, expected', [
        (INPUT_3, 82892753),
        (INPUT_4, 5586022),
        (INPUT_5, 460664),
    ]
)
def test_compute(input_s, expected):
    assert compute(input_s) == expected


INPUT = """
9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL
""".strip()


def main() -> int:
    with open('day14.txt') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
