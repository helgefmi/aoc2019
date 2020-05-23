#!/usr/bin/env python3
import random
from enum import Enum
from typing import List

import pytest

import part1 # noqa

Deck = List[int]


# Snippet stolen from https://stackoverflow.com/questions/4798654/modular-multiplicative-inverse-function-in-python.
# Had no idea this existed. Almost googled something along the lines of "inverse with modulus" at some point,
# but concluded that it's not possible to do such a thing, and went on to spend hours on dead ends instead.
# Then gave up and learned you had to know about modular inverse to solve this one.
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


class Technique(Enum):
    REVERSE = 0
    CUT = 1
    DEAL = 2


def parse_techniques(cts):
    techs = []
    for line in cts.splitlines():
        if line == 'deal into new stack':
            techs.append((Technique.REVERSE, None))
        elif line.startswith('cut '):
            n = int(line[4:])
            techs.append((Technique.CUT, n))
        else:
            assert line.startswith('deal with increment ')
            n = int(line.split('increment ')[1])
            techs.append((Technique.DEAL, n))
    return techs


def optimize_techniques(techs, num_cards):
    # Simplifies a list of techniques (input.txt is made into only 2 lines)
    while True:
        for i in range(len(techs) - 1):
            left_tech, left_n = techs[i]
            right_tech, right_n = techs[i + 1]

            if left_tech == Technique.REVERSE == right_tech:
                techs.pop(i)
                techs.pop(i)
                break

            if left_tech == Technique.CUT == right_tech:
                techs.pop(i)
                techs[i] = Technique.CUT, (left_n + right_n) % num_cards
                break

            if left_tech == Technique.DEAL == right_tech:
                techs.pop(i)
                techs[i] = Technique.DEAL, (left_n * right_n) % num_cards
                break

            if left_tech == Technique.REVERSE and right_tech == Technique.DEAL:
                techs[i] = (Technique.DEAL, right_n)
                techs[i + 1] = (Technique.CUT, -(right_n - 1))
                techs.insert(i + 2, (Technique.REVERSE, None))
                break

            if right_tech == Technique.DEAL:
                if left_tech == Technique.CUT:
                    techs[i] = right_tech, right_n
                    techs[i + 1] = left_tech, (left_n * right_n) % num_cards
                    break

            if right_tech == Technique.CUT:
                if left_tech == Technique.REVERSE:
                    techs[i] = (Technique.CUT, num_cards - right_n)
                    techs[i + 1] = (Technique.REVERSE, None)
                    break
        else:
            break

    return techs


class Shuffler:
    def __init__(self, techniques, num_cards: int, reverse: bool = False):
        self.num_cards = num_cards
        self.techniques = techniques
        self.reverse = reverse

        if self.reverse:
            self.techniques.reverse()

    def shuffle_deck(self, cards: List[int]) -> List[int]:
        new_cards = [-1] * self.num_cards
        for i in range(self.num_cards):
            i2 = self.shuffle_card(i)
            new_cards[i2] = cards[i]
        cards = new_cards
        return new_cards

    def shuffle_card(self, card: int) -> int:
        for tech, n in self.techniques:
            if tech == Technique.REVERSE:
                card = self.tech_deal_into_new_stack(card)
            elif tech == Technique.CUT:
                card = self.tech_cut(card, n)
            elif tech == Technique.DEAL:
                card = self.tech_deal_with_increment(card, n)
        return card

    def tech_deal_into_new_stack(self, card: int) -> int:
        return (-1 - card) % self.num_cards

    def tech_cut(self, card: int, n: int) -> int:
        if self.reverse:
            n = -n
        return (card - n) % self.num_cards

    def tech_deal_with_increment(self, card: int, n: int) -> int:
        if self.reverse:
            # See comment at start of file
            return (card * modinv(n, self.num_cards)) % self.num_cards
        return (card * n) % self.num_cards


def compute_card(cts: str, card: int, num_cards: int) -> int:
    techniques = optimize_techniques(parse_techniques(cts), num_cards)
    shuffler = Shuffler(techniques, num_cards,)
    return shuffler.shuffle_card(card)


def compute_deck(cts: str, cards: List[int]):
    techniques = optimize_techniques(parse_techniques(cts), len(cards))
    shuffler = Shuffler(techniques, len(cards))
    return shuffler.shuffle_deck(cards)


def compute(cts: str):
    card_len = 119315717514047

    techniques = optimize_techniques(parse_techniques(cts), card_len)

    # populate tech_doubles with [(1, tech_for_1_shuffle), (2, tech_for_2_shuffles), (4, ..), ..]
    tech_doubles = []
    i = 1
    while i <= card_len:
        tech_doubles.append((i, techniques))
        techniques = optimize_techniques(techniques * 2, card_len)
        i *= 2

    # Start with card = 2020, and shuffle backwards (reverse=True) until `shuffles_left == 0`
    card = 2020
    shuffles_left = 101741582076661
    for double, techniques in tech_doubles[::-1]:
        shuffler = Shuffler(techniques, card_len, reverse=True)
        while shuffles_left - double >= 0:
            card = shuffler.shuffle_card(card)
            print(double, shuffles_left, card)
            shuffles_left -= double

    assert shuffles_left == 0
    return card


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
    'input_str, expected', [
        (INPUT_1, [0, 3, 6, 9, 2, 5, 8, 1, 4, 7]),
        (INPUT_2, [3, 0, 7, 4, 1, 8, 5, 2, 9, 6]),
        (INPUT_3, [6, 3, 0, 7, 4, 1, 8, 5, 2, 9]),
        (INPUT_4, [9, 2, 5, 8, 1, 4, 7, 0, 3, 6]),
    ]
)
def test_compute_deck(input_str: str, expected: List[int]) -> None:
    cards = compute_deck(input_str, list(range(len(expected))))
    assert cards == expected
    # TODO
    # assert compute_deck(input_str, expected, True) == list(range(10))


def test_tech_deal_into_new_stack():
    N = 10007
    cards = list(range(N))
    random.shuffle(cards)

    expected = cards[::-1]

    for n in [1, 3, 9, 99]:
        cts = 'deal into new stack\n' * n
        techniques = optimize_techniques(parse_techniques(cts), N)
        shuffler = Shuffler(techniques, N)
        assert shuffler.shuffle_deck(cards) == expected


def test_tech_cut():
    N = 10007
    cards = list(range(N))
    random.shuffle(cards)

    for _ in range(100):
        n = random.randrange(-N + 1, N - 1)
        expected = cards[n:] + cards[:n]
        cts = 'cut {}'.format(n)

        techniques = optimize_techniques(parse_techniques(cts), N)
        shuffler = Shuffler(techniques, N)
        new_cards = shuffler.shuffle_deck(cards)
        assert new_cards == expected


def test_tech_deal_with_increment():
    N = 10007
    cards = list(range(N))
    random.shuffle(cards)

    for n in [
        10, 12, 13, 14, 15, 17, 2, 24, 28, 29, 31, 34, 35, 36, 40, 41,
        43, 44, 45, 46, 48, 5, 51, 53, 54, 56, 61, 64, 66, 7, 72, 75
    ]:
        expected = part1.tech_deal_with_increment(cards, n)
        cts = 'deal with increment {}'.format(n)
        techniques = optimize_techniques(parse_techniques(cts), N)
        shuffler = Shuffler(techniques, N)
        assert shuffler.shuffle_deck(cards) == expected


def assert_reverse(cts, initial_cards):
    card_len = len(initial_cards)

    techniques = optimize_techniques(parse_techniques(cts), card_len)

    shuffler = Shuffler(techniques, card_len)
    shuffled = shuffler.shuffle_deck(initial_cards)

    shuffler = Shuffler(techniques, card_len, True)
    shuffled_rev = shuffler.shuffle_deck(shuffled)

    assert shuffled_rev == initial_cards


def test_reverse_cut():
    cards = list(range(10))
    assert_reverse('cut 4', cards)
    assert_reverse('cut -4', cards)

    cards = list(range(107))
    for x in range(-100, 100):
        assert_reverse('cut {}'.format(x), cards)

    cards = list(range(10007))
    assert_reverse('cut 10006', cards)
    assert_reverse('cut -10006', cards)


def test_reverse_deal():
    cards = list(range(10007))
    for n in [
        2, 5, 7, 10, 12, 13, 14, 15, 17, 24, 28, 29, 31, 34, 35, 36,
        40, 41, 43, 44, 45, 46, 48, 51, 53, 54, 56, 61, 64, 66, 72, 75
    ]:
        assert_reverse('deal with increment {}'.format(n), cards)


def main() -> int:
    with open('input.txt', 'r') as f:
        cts = f.read().strip()

    print(compute(cts))

    return 0


if __name__ == '__main__':
    exit(main())
