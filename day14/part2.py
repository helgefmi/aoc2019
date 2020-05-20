#!/usr/bin/env python
from copy import deepcopy
import pytest


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


def simplify(rules):
    rules = deepcopy(rules)

    for key, data in list(rules.items()):
        if key == 'ORE' or 'ORE' in data['children'].keys():
            continue
        for child_name, child_val in list(data['children'].items()):
            child_data = rules[child_name]
            if child_data['makes'] < child_val and child_val % child_data['makes'] == 0:
                data['children'].pop(child_name)
                for child2_name, child2_val in child_data['children'].items():
                    data['children'].setdefault(child2_name, 0)
                    data['children'][child2_name] += (child_val * child2_val) // child_data['makes']

    all_children = set(child_name for data in rules.values() for child_name in data['children'])
    to_remove = set(rules.keys()) - all_children - set(['FUEL'])
    for key in to_remove:
        rules.pop(key)

    return rules


def compute(cts):
    rules = input_to_rules(cts)

    while True:
        rules, last_rules = simplify(rules), rules
        if rules == last_rules:
            break

    key_map = dict((k, i) for i, k in enumerate(rules))
    key_map_rev = dict((v, k) for k, v in key_map.items())

    ORE = len(rules)
    key_map['ORE'] = ORE
    key_map_rev[ORE] = 'ORE'

    makes = []
    children = []
    for i in range(len(rules)):
        k = key_map_rev[i]
        makes.append(rules[k]['makes'])
        rules_children = rules[k]['children']
        children.append([(key_map[k2], v) for k2, v in rules_children.items()])

    makes = tuple(makes)
    children = tuple(children)

    inv = [0] * len(rules)

    def recurse(prod_name):
        ores_needed = 0

        for other_name, other_num in children[prod_name]:
            if other_name == ORE:
                ores_needed += other_num
            else:
                while inv[other_name] < other_num:
                    new_ores = recurse(other_name)
                    ores_needed += new_ores
                inv[other_name] -= other_num

        inv[prod_name] += makes[prod_name]

        return ores_needed

    ores_left = 1000000000000
    ores_spent = 0
    num_fuels = 0

    while True:
        ores_needed = recurse(key_map['FUEL'])
        ores_spent += ores_needed
        ores_left -= ores_needed
        if ores_left <= 0:
            break
        num_fuels += 1

    return num_fuels


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


def main() -> int:
    with open('day14.txt') as f:
        cts = f.read()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
