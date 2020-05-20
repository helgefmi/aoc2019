#!/usr/bin/env python3
import pytest

from typing import Iterable


def meets_criteria(n: int) -> bool:
    digits = list(map(int, str(n)))
    zipped = list(zip(digits, digits[1:]))

    if not all(nex >= cur for cur, nex in zipped):
        return False

    return any(cur == nex for cur, nex in zipped)


def compute(input_range: Iterable[int]) -> int:
    return len(list(filter(meets_criteria, input_range)))


@pytest.mark.parametrize(
    'input_i, expected', [
        (111111, True),
        (223450, False),
        (123789, False),
    ]
)
def test_compute(input_i: int, expected: bool) -> None:
    assert meets_criteria(input_i) == expected


def main() -> int:
    print(compute(range(353096, 843212)))

    return 0


if __name__ == '__main__':
    exit(main())
