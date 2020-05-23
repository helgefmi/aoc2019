#!/usr/bin/env python3
from typing import List

import pytest


def tech_deal_into_new_stack(cards):
    return cards[::-1]


def tech_cut(cards, n):
    return cards[n:] + cards[:n]


def tech_deal_with_increment(cards, n):
    num_cards = len(cards)
    new_deck = [None] * num_cards

    for i, card in enumerate(cards):
        new_i = (n * i) % num_cards
        new_deck[new_i] = card

    return new_deck


def parse_instruction(line: str):
    if line == 'deal into new stack':
        return tech_deal_into_new_stack, []
    elif line.startswith('cut '):
        return tech_cut, [int(line[4:])]
    elif line.startswith('deal with increment '):
        return tech_deal_with_increment, [int(line.split('increment ')[1])]


def compute(cts: str, num_cards: int) -> List[int]:
    cards = list(range(num_cards))
    for line in cts.splitlines():
        fn, args = parse_instruction(line)
        cards = fn(cards, *args)
    return cards


INPUT_1 = """
deal with increment 7
deal into new stack
deal into new stack
""".strip()

INPUT_2 = """
cut 6
deal with increment 7
deal into new stack
""".strip()

INPUT_3 = """
deal with increment 7
deal with increment 9
cut -2
""".strip()

INPUT_4 = """
deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1
""".strip()


@pytest.mark.parametrize(
    'input_str, num_cards, expected', [
        (INPUT_1, 10, [0, 3, 6, 9, 2, 5, 8, 1, 4, 7]),
        (INPUT_2, 10, [3, 0, 7, 4, 1, 8, 5, 2, 9, 6]),
        (INPUT_3, 10, [6, 3, 0, 7, 4, 1, 8, 5, 2, 9]),
        (INPUT_4, 10, [9, 2, 5, 8, 1, 4, 7, 0, 3, 6]),
    ]
)
def test_compute(input_str: str, num_cards: int, expected: List[int]) -> None:
    assert compute(input_str, num_cards) == expected


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    cards = compute(cts, 10007)
    print(cards.index(2019))

    return 0


if __name__ == '__main__':
    exit(main())
