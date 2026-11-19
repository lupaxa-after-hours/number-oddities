"""Integer facts shared by every property checker.

Factorisation uses integer trial division. A skipped factorisation is not a
claim that the number is prime or composite.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lupaxa.number_oddities.properties import Property

from lupaxa.number_oddities.limits import COMPLETE_LIMIT, FACTOR_TRIAL_LIMIT

Status = str


@dataclass(frozen=True)
class Facts:
    """Digits and, when affordable, the prime factorisation of one integer."""

    number: int
    digits: tuple[int, ...]
    factor_status: str
    factors: tuple[int, ...]
    search: bool = False


def digits_of(number: int) -> tuple[int, ...]:
    """Return the decimal digits of ``abs(number)``, with ``0`` as ``(0,)``."""
    value = abs(number)
    if value == 0:
        return (0,)
    found: list[int] = []
    while value:
        found.append(value % 10)
        value //= 10
    return tuple(reversed(found))


def digit_sum(number: int) -> int:
    """Return the sum of the decimal digits of ``abs(number)``."""
    return sum(digits_of(number))


def is_square(number: int) -> bool:
    """Return whether ``number`` is the square of an integer."""
    if number < 0:
        return False
    root = math.isqrt(number)
    return root * root == number


def square_root(number: int) -> int:
    """Return the integer square root of a perfect square."""
    return math.isqrt(number)


def cube_root(number: int) -> int:
    """Return the integer cube root of ``abs(number)``."""
    value = abs(number)
    low = 0
    high = 1
    while high * high * high <= value:
        high *= 2
    while low + 1 < high:
        mid = (low + high) // 2
        if mid * mid * mid <= value:
            low = mid
        else:
            high = mid
    return low


def is_cube(number: int) -> bool:
    """Return whether ``number`` is the cube of an integer."""
    root = cube_root(number)
    if number < 0:
        return (-root) * (-root) * (-root) == number
    return root * root * root == number


def factorise(number: int, *, search: bool = False) -> tuple[str, tuple[int, ...]]:
    """Factor ``abs(number)``.

    Returns ``("complete", factors)`` or ``("skipped", partial)``.
    ``1`` and ``0`` are complete and have no prime factors. During a range
    search, integers above ``COMPLETE_LIMIT`` are skipped immediately.
    """
    value = abs(number)
    if value <= 1:
        return ("complete", ())
    if search and value > COMPLETE_LIMIT:
        return ("skipped", ())
    if value <= COMPLETE_LIMIT:
        return _trial(value, math.isqrt(value))
    return _trial(value, FACTOR_TRIAL_LIMIT)


def _trial(value: int, limit: int) -> tuple[str, tuple[int, ...]]:
    factors: list[int] = []
    while value % 2 == 0:
        factors.append(2)
        value //= 2
        if value == 1:
            return ("complete", tuple(factors))
    divisor = 3
    while divisor <= limit and divisor * divisor <= value:
        while value % divisor == 0:
            factors.append(divisor)
            value //= divisor
        divisor += 2
    if value == 1:
        return ("complete", tuple(factors))
    if value <= limit or math.isqrt(value) <= limit:
        factors.append(value)
        return ("complete", tuple(factors))
    return ("skipped", tuple(factors))


def divisor_sum(factors: tuple[int, ...]) -> int:
    """Return the sum of all positive divisors from a complete factorisation."""
    if not factors:
        return 1
    total = 1
    index = 0
    while index < len(factors):
        prime = factors[index]
        power = 0
        while index < len(factors) and factors[index] == prime:
            power += 1
            index += 1
        total *= (prime ** (power + 1) - 1) // (prime - 1)
    return total


def proper_divisor_sum(number: int, factors: tuple[int, ...]) -> int:
    """Return the sum of proper divisors, excluding the number itself."""
    if number <= 1:
        return 0
    return divisor_sum(factors) - number


def prime_status(number: int, *, search: bool = False) -> str:
    """Return ``match``, ``miss``, or ``skipped`` for a primality test."""
    if number <= 1:
        return "miss"
    status, factors = factorise(number, search=search)
    if status != "complete":
        return "skipped"
    if factors == (number,):
        return "match"
    return "miss"


def facts_for(number: int, *, search: bool = False, factor: bool = True) -> Facts:
    """Build the digit and factor facts for one integer."""
    if factor:
        status, factors = factorise(number, search=search)
    else:
        status, factors = ("not_needed", ())
    return Facts(number, digits_of(number), status, factors, search)


def sign_of(number: int) -> str:
    """Return ``negative``, ``zero``, or ``positive``."""
    if number < 0:
        return "negative"
    if number == 0:
        return "zero"
    return "positive"


def parity_of(number: int) -> str:
    """Return ``even`` or ``odd``."""
    return "even" if number % 2 == 0 else "odd"


def inspect_number(number: int) -> tuple[Facts, list[tuple[Property, Facts]], list[str]]:
    """Return factor facts, matching properties, and skipped property ids."""
    from lupaxa.number_oddities.properties import matching

    found, skipped, shared = matching(number)
    return shared, found, skipped


def find_numbers(prop: Property, start: int, end: int, *, limit: int | None) -> list[int]:
    """Return matching integers in ascending order.

    A ``limit`` stops the scan once that many matches have been found.
    Pass ``None`` to scan the whole range.
    """
    found: list[int] = []
    for number in range(start, end + 1):
        facts = facts_for(number, search=True, factor=prop.needs_factors)
        if prop.check(facts) == "match":
            found.append(number)
            if limit is not None and len(found) >= limit:
                break
    return found
