#!/usr/bin/env python3
from collections import defaultdict

from typing import Iterable, Dict

import pytest


def meets_criteria(n: int) -> bool:
    digits = list(map(int, str(n)))
    zipped = list(zip(digits, digits[1:]))

    if not all(nex >= cur for cur, nex in zipped):
        return False

    num_of_value: Dict[int, int] = defaultdict(int)
    for cur in digits:
        num_of_value[cur] += 1

    for count in num_of_value.values():
        if count == 2:
            return True

    return False


def compute(input_range: Iterable[int]) -> int:
    return len(list(filter(meets_criteria, input_range)))


@pytest.mark.parametrize(
    'input_i, expected', [
        (112233, True),
        (123444, False),
        (111122, True),
        (111222, False),
        (123456, False),
        (113456, True),
        (122456, True),
        (123356, True),
        (123446, True),
        (123455, True),
        (123333, False),
    ]
)
def test_compute(input_i: int, expected: bool) -> None:
    assert meets_criteria(input_i) == expected


def main() -> int:
    print(compute(range(353096, 843212)))

    return 0


if __name__ == '__main__':
    exit(main())
