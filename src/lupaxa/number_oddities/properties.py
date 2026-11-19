"""The thirty-eight Number Oddities properties, their checks, and their explanations.

A checker returns ``match``, ``miss``, or ``skipped``. ``skipped`` means the
calculation was not finished. It is not a negative result.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from lupaxa.number_oddities.analysis import (
    Facts,
    digit_sum,
    digits_of,
    facts_for,
    is_cube,
    is_square,
    proper_divisor_sum,
    square_root,
)
from lupaxa.number_oddities.curiosities import (
    _amicable,
    _catalan,
    _dudeney,
    _emirp,
    _explain_amicable,
    _explain_catalan,
    _explain_dudeney,
    _explain_emirp,
    _explain_factorial,
    _explain_factorion,
    _explain_hoax,
    _explain_keith,
    _explain_lucas,
    _explain_munchhausen,
    _explain_pell,
    _explain_primorial,
    _explain_semiprime,
    _explain_sophie,
    _explain_sphenic,
    _explain_spy,
    _explain_taxicab,
    _explain_trimorphic,
    _explain_vampire,
    _explain_zuckerman,
    _factorial,
    _factorion,
    _hoax,
    _keith,
    _lucas,
    _munchhausen,
    _pell,
    _primorial,
    _semiprime,
    _sophie,
    _sphenic,
    _spy,
    _taxicab,
    _trimorphic,
    _vampire,
    _zuckerman,
)

Status = str
_SUPERS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _power(base: int, exponent: int, *, ascii_math: bool) -> str:
    if ascii_math:
        return f"{base}^{exponent}"
    return f"{base}{str(exponent).translate(_SUPERS)}"


def _join(parts: list[str]) -> str:
    return " + ".join(parts)


def _times(factors: tuple[int, ...], *, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    return f" {mark} ".join(str(factor) for factor in factors)


@dataclass(frozen=True)
class Property:
    """One mathematical property and the text used to explain a match."""

    ident: str
    title: str
    description: str
    examples: tuple[int, ...]
    check: Callable[[Facts], Status]
    explain: Callable[[Facts, bool], str]
    needs_factors: bool = False


def _prime(facts: Facts) -> Status:
    number = facts.number
    if number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    return "match" if facts.factors == (number,) else "miss"


def _composite(facts: Facts) -> Status:
    number = facts.number
    if number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    return "match" if facts.factors != (number,) else "miss"


def _abundance(facts: Facts) -> int | None:
    number = facts.number
    if number <= 0 or facts.factor_status != "complete":
        return None
    return proper_divisor_sum(number, facts.factors)


def _perfect(facts: Facts) -> Status:
    total = _abundance(facts)
    if facts.number <= 0:
        return "miss"
    if total is None:
        return "skipped"
    return "match" if total == facts.number else "miss"


def _abundant(facts: Facts) -> Status:
    total = _abundance(facts)
    if facts.number <= 0:
        return "miss"
    if total is None:
        return "skipped"
    return "match" if total > facts.number else "miss"


def _deficient(facts: Facts) -> Status:
    total = _abundance(facts)
    if facts.number <= 0:
        return "miss"
    if total is None:
        return "skipped"
    return "match" if total < facts.number else "miss"


def _square(facts: Facts) -> Status:
    return "match" if is_square(facts.number) else "miss"


def _cube(facts: Facts) -> Status:
    return "match" if is_cube(facts.number) else "miss"


def _triangular(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    return "match" if is_square(8 * facts.number + 1) else "miss"


def _pronic(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    root = square_root(facts.number)
    return "match" if root * (root + 1) == facts.number else "miss"


def _fibonacci(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    square = facts.number * facts.number
    return "match" if is_square(5 * square + 4) or is_square(5 * square - 4) else "miss"


def _palindromic(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    text = "".join(str(digit) for digit in facts.digits)
    return "match" if text == text[::-1] else "miss"


def _automorphic(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    return "match" if str(facts.number * facts.number).endswith(str(facts.number)) else "miss"


def _harshad(facts: Facts) -> Status:
    if facts.number <= 0:
        return "miss"
    total = sum(facts.digits)
    if total == 0:
        return "miss"
    return "match" if facts.number % total == 0 else "miss"


def _armstrong(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    power = len(facts.digits)
    return "match" if sum(digit**power for digit in facts.digits) == facts.number else "miss"


def _disarium(facts: Facts) -> Status:
    if facts.number < 0:
        return "miss"
    total = sum(digit ** (index + 1) for index, digit in enumerate(facts.digits))
    return "match" if total == facts.number else "miss"


def _kaprekar(facts: Facts) -> Status:
    if facts.number <= 0:
        return "miss"
    if facts.number == 1:
        return "match"
    text = str(facts.number * facts.number)
    for index in range(1, len(text)):
        right = int(text[index:])
        if right and int(text[:index]) + right == facts.number:
            return "match"
    return "miss"


def _happy(facts: Facts) -> Status:
    if facts.number <= 0:
        return "miss"
    return "match" if _happy_steps(facts.number)[-1] == 1 else "miss"


def _smith(facts: Facts) -> Status:
    if facts.number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    if facts.factors == (facts.number,):
        return "miss"
    factor_digits = sum(digit_sum(factor) for factor in facts.factors)
    return "match" if factor_digits == sum(facts.digits) else "miss"


def _happy_steps(number: int) -> list[int]:
    seen: set[int] = set()
    steps = [number]
    while number not in seen and number != 1:
        seen.add(number)
        number = sum(digit * digit for digit in digits_of(number))
        steps.append(number)
        if number == 4:
            break
    return steps


def _explain_prime(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    return f"{facts.number} is prime. Its only positive divisors are 1 and {facts.number}."


def _explain_composite(facts: Facts, ascii_math: bool) -> str:
    shown = _times(facts.factors, ascii_math=ascii_math)
    return f"{facts.number} = {shown}\n\n{facts.number} is composite."


def _explain_perfect(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    total = proper_divisor_sum(facts.number, facts.factors)
    return (
        f"The proper divisors of {facts.number} sum to {total}.\n\n"
        f"{facts.number} is a perfect number."
    )


def _explain_abundant(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    total = proper_divisor_sum(facts.number, facts.factors)
    return (
        f"The proper divisors of {facts.number} sum to {total}, "
        f"which is greater than {facts.number}.\n\n"
        f"{facts.number} is an abundant number."
    )


def _explain_deficient(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    total = proper_divisor_sum(facts.number, facts.factors)
    return (
        f"The proper divisors of {facts.number} sum to {total}, "
        f"which is less than {facts.number}.\n\n"
        f"{facts.number} is a deficient number."
    )


def _explain_square(facts: Facts, ascii_math: bool) -> str:
    root = square_root(facts.number)
    shown = _power(root, 2, ascii_math=ascii_math)
    return f"{shown} = {facts.number}\n\n{facts.number} is a perfect square."


def _explain_cube(facts: Facts, ascii_math: bool) -> str:
    root = cube_root_signed(facts.number)
    shown = _power(root, 3, ascii_math=ascii_math)
    return f"{shown} = {facts.number}\n\n{facts.number} is a perfect cube."


def cube_root_signed(number: int) -> int:
    """Return the signed integer cube root of a perfect cube."""
    from lupaxa.number_oddities.analysis import cube_root

    root = cube_root(number)
    return -root if number < 0 else root


def _explain_triangular(facts: Facts, ascii_math: bool) -> str:
    discriminant = square_root(8 * facts.number + 1)
    index = (discriminant - 1) // 2
    mark = "*" if ascii_math else "×"
    return (
        f"{index} {mark} {index + 1} / 2 = {facts.number}\n\n{facts.number} is a triangular number."
    )


def _explain_pronic(facts: Facts, ascii_math: bool) -> str:
    root = square_root(facts.number)
    mark = "*" if ascii_math else "×"
    return f"{root} {mark} {root + 1} = {facts.number}\n\n{facts.number} is a pronic number."


def _explain_fibonacci(facts: Facts, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    square = "^2" if ascii_math else "²"
    plus = is_square(5 * facts.number * facts.number + 4)
    witness = "+ 4" if plus else "- 4"
    return (
        f"5 {mark} {facts.number}{square} {witness} is a perfect square.\n\n"
        f"{facts.number} is a Fibonacci number."
    )


def _explain_palindromic(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    text = str(facts.number)
    return f"{text} reversed is {text[::-1]}.\n\n{facts.number} is palindromic."


def _explain_automorphic(facts: Facts, ascii_math: bool) -> str:
    square = facts.number * facts.number
    shown = _power(facts.number, 2, ascii_math=ascii_math)
    return (
        f"{shown} = {square}\n{square} ends with {facts.number}.\n\n{facts.number} is automorphic."
    )


def _explain_harshad(facts: Facts, ascii_math: bool) -> str:
    total = sum(facts.digits)
    quotient = facts.number // total
    mark = "/" if ascii_math else "÷"
    return (
        f"{_join([str(digit) for digit in facts.digits])} = {total}\n"
        f"{facts.number} {mark} {total} = {quotient}\n\n"
        f"{facts.number} is a Harshad number."
    )


def _explain_power_sum(
    facts: Facts, ascii_math: bool, power_of: Callable[[int, int], int], title: str, article: str
) -> str:
    terms = []
    values = []
    for index, digit in enumerate(facts.digits):
        exponent = power_of(index, len(facts.digits))
        terms.append(_power(digit, exponent, ascii_math=ascii_math))
        values.append(digit**exponent)
    lines = [_join(terms)]
    if len(values) > 1:
        lines.append(f"= {_join([str(value) for value in values])}")
    lines.append(f"= {sum(values)}")
    return "\n".join(lines) + f"\n\n{facts.number} is {article} {title} number."


def _explain_armstrong(facts: Facts, ascii_math: bool) -> str:
    return _explain_power_sum(
        facts,
        ascii_math,
        lambda _index, count: count,
        "Armstrong",
        "an",
    )


def _explain_disarium(facts: Facts, ascii_math: bool) -> str:
    return _explain_power_sum(
        facts,
        ascii_math,
        lambda index, _count: index + 1,
        "Disarium",
        "a",
    )


def _explain_kaprekar(facts: Facts, ascii_math: bool) -> str:
    shown = _power(facts.number, 2, ascii_math=ascii_math)
    text = str(facts.number * facts.number)
    if facts.number == 1:
        return f"{shown} = 1\n0 + 1 = 1\n\n1 is a Kaprekar number."
    left, right = _kaprekar_split(facts.number, text)
    return (
        f"{shown} = {text}\n"
        f"{left} + {right} = {facts.number}\n\n"
        f"{facts.number} is a Kaprekar number."
    )


def _kaprekar_split(number: int, text: str) -> tuple[int, int]:
    for index in range(1, len(text)):
        right = int(text[index:])
        left = int(text[:index])
        if right and left + right == number:
            return left, right
    return 0, number


def _explain_happy(facts: Facts, ascii_math: bool) -> str:
    steps = _happy_steps(facts.number)
    lines = []
    for value in steps[:-1]:
        parts = digits_of(value)
        terms = [_power(digit, 2, ascii_math=ascii_math) for digit in parts]
        squares = [digit * digit for digit in parts]
        lines.append(f"{_join(terms)} = {_join([str(item) for item in squares])} = {sum(squares)}")
    return "\n".join(lines) + f"\n\n{facts.number} is a happy number."


def _explain_smith(facts: Facts, ascii_math: bool) -> str:
    shown = _times(facts.factors, ascii_math=ascii_math)
    number_digits = _join([str(digit) for digit in facts.digits])
    factor_digits = _join([str(digit) for factor in facts.factors for digit in digits_of(factor)])
    return (
        f"{facts.number} = {shown}\n"
        f"{number_digits} = {sum(facts.digits)}\n"
        f"{factor_digits} = {sum(digit_sum(factor) for factor in facts.factors)}\n\n"
        f"{facts.number} is a Smith number."
    )


REGISTRY: tuple[Property, ...] = (
    Property(
        "prime",
        "Prime",
        "An integer greater than 1 whose only positive divisors are 1 and itself.",
        (2, 3, 5, 7, 11),
        _prime,
        _explain_prime,
        True,
    ),
    Property(
        "composite",
        "Composite",
        "An integer greater than 1 that is not prime. 1 is neither prime nor composite.",
        (4, 6, 8, 9, 12),
        _composite,
        _explain_composite,
        True,
    ),
    Property(
        "perfect",
        "Perfect",
        "A positive integer equal to the sum of its proper divisors.",
        (28, 6, 496),
        _perfect,
        _explain_perfect,
        True,
    ),
    Property(
        "abundant",
        "Abundant",
        "A positive integer whose proper divisors sum to more than the integer.",
        (12, 18, 20, 24),
        _abundant,
        _explain_abundant,
        True,
    ),
    Property(
        "deficient",
        "Deficient",
        "A positive integer whose proper divisors sum to less than the integer.",
        (1, 2, 3, 4, 8),
        _deficient,
        _explain_deficient,
        True,
    ),
    Property(
        "perfect_square",
        "Perfect square",
        "An integer that is the square of an integer. Negatives are not squares.",
        (0, 1, 4, 9, 36),
        _square,
        _explain_square,
    ),
    Property(
        "perfect_cube",
        "Perfect cube",
        "An integer that is the cube of an integer, including negative cubes.",
        (0, 1, -8, 8, 27),
        _cube,
        _explain_cube,
    ),
    Property(
        "triangular",
        "Triangular",
        "A number of the form k(k + 1) / 2 for an integer k >= 0. 0 and 1 qualify.",
        (0, 1, 36, 28, 10),
        _triangular,
        _explain_triangular,
    ),
    Property(
        "pronic",
        "Pronic",
        "A number of the form k(k + 1) for an integer k >= 0. 0 qualifies. 1 does not.",
        (0, 2, 6, 12, 20),
        _pronic,
        _explain_pronic,
    ),
    Property(
        "fibonacci",
        "Fibonacci",
        "A non-negative Fibonacci number. 0 and 1 are included.",
        (0, 1, 2, 8, 13),
        _fibonacci,
        _explain_fibonacci,
    ),
    Property(
        "palindromic",
        "Palindromic",
        "A non-negative integer whose decimal digits read the same forwards and backwards.",
        (0, 1, 11, 121),
        _palindromic,
        _explain_palindromic,
    ),
    Property(
        "automorphic",
        "Automorphic",
        "A non-negative integer whose square ends with the integer itself.",
        (0, 1, 5, 6, 25),
        _automorphic,
        _explain_automorphic,
    ),
    Property(
        "harshad",
        "Harshad",
        "A positive integer divisible by the sum of its decimal digits.",
        (153, 18, 24, 1),
        _harshad,
        _explain_harshad,
    ),
    Property(
        "armstrong",
        "Armstrong",
        "A non-negative integer equal to the sum of its digits raised to the number of digits.",
        (153, 370, 371, 0, 1),
        _armstrong,
        _explain_armstrong,
    ),
    Property(
        "disarium",
        "Disarium",
        "A non-negative integer equal to the sum of its digits raised to their positions.",
        (135, 175, 518, 0, 1),
        _disarium,
        _explain_disarium,
    ),
    Property(
        "kaprekar",
        "Kaprekar",
        "A positive integer whose square can be split into two parts that add up to it.",
        (45, 9, 55, 297, 1),
        _kaprekar,
        _explain_kaprekar,
    ),
    Property(
        "happy",
        "Happy",
        "A positive integer that reaches 1 by repeatedly summing the squares of its digits.",
        (19, 7, 10, 13, 1),
        _happy,
        _explain_happy,
    ),
    Property(
        "smith",
        "Smith",
        "A composite number whose digits sum to the same total as the digits of its prime factors.",
        (666, 4, 22, 27),
        _smith,
        _explain_smith,
        True,
    ),
    Property(
        "factorion",
        "Factorion",
        "A positive integer equal to the sum of the factorials of its digits.",
        (145, 1, 2, 40585),
        _factorion,
        _explain_factorion,
    ),
    Property(
        "dudeney",
        "Dudeney",
        "A non-negative cube whose digits sum to the cube root.",
        (512, 1, 4913, 5832),
        _dudeney,
        _explain_dudeney,
    ),
    Property(
        "keith",
        "Keith",
        "A multi-digit number that appears in the sequence started by its own digits.",
        (14, 19, 28, 47),
        _keith,
        _explain_keith,
    ),
    Property(
        "trimorphic",
        "Trimorphic",
        "A non-negative integer whose cube ends with the integer itself.",
        (25, 0, 1, 76),
        _trimorphic,
        _explain_trimorphic,
    ),
    Property(
        "zuckerman",
        "Zuckerman",
        "A positive integer divisible by the product of its digits, none of which is 0.",
        (135, 24, 12, 11),
        _zuckerman,
        _explain_zuckerman,
    ),
    Property(
        "spy",
        "Spy",
        "At least two digits, and the sum of those digits equals their product.",
        (123, 22, 1124),
        _spy,
        _explain_spy,
    ),
    Property(
        "hoax",
        "Hoax",
        "A composite whose digits sum like the digits of its distinct prime factors.",
        (22, 58, 84, 94),
        _hoax,
        _explain_hoax,
        True,
    ),
    Property(
        "amicable",
        "Amicable",
        "The proper-divisor sum is a different number that sums back to this one.",
        (220, 284, 1184, 1210),
        _amicable,
        _explain_amicable,
        True,
    ),
    Property(
        "vampire",
        "Vampire",
        "An even-digit number equal to two fangs that use exactly those digits.",
        (1260, 1395, 1435),
        _vampire,
        _explain_vampire,
    ),
    Property(
        "taxicab",
        "Taxicab",
        "A positive integer that is a sum of two positive cubes in two ways.",
        (1729, 4104, 13832),
        _taxicab,
        _explain_taxicab,
    ),
    Property(
        "emirp",
        "Emirp",
        "A non-palindromic prime whose digit reversal is also prime.",
        (13, 17, 37, 31),
        _emirp,
        _explain_emirp,
        True,
    ),
    Property(
        "munchhausen",
        "Munchhausen",
        "A positive integer equal to the sum of its digits raised to themselves. 0^0 is 0.",
        (3435, 1, 438579088),
        _munchhausen,
        _explain_munchhausen,
    ),
    Property(
        "lucas",
        "Lucas",
        "A Lucas number: 2, 1, then each term is the sum of the previous two.",
        (7, 1, 2, 4),
        _lucas,
        _explain_lucas,
    ),
    Property(
        "catalan",
        "Catalan",
        "A Catalan number. 1, 2, 5, 14, 42, and so on.",
        (14, 1, 2, 5),
        _catalan,
        _explain_catalan,
    ),
    Property(
        "pell",
        "Pell",
        "A Pell number: 0, 1, then twice the last term plus the one before.",
        (5, 0, 1, 2),
        _pell,
        _explain_pell,
    ),
    Property(
        "factorial",
        "Factorial",
        "A factorial k! for some integer k >= 0.",
        (24, 1, 2, 6),
        _factorial,
        _explain_factorial,
    ),
    Property(
        "primorial",
        "Primorial",
        "A product of the first k primes, for some k >= 1.",
        (30, 2, 6, 210),
        _primorial,
        _explain_primorial,
    ),
    Property(
        "sophie_germain",
        "Sophie Germain prime",
        "A prime p for which 2p + 1 is also prime.",
        (11, 2, 3, 5),
        _sophie,
        _explain_sophie,
        True,
    ),
    Property(
        "semiprime",
        "Semiprime",
        "A product of exactly two primes, counting a repeated prime.",
        (15, 4, 6, 9),
        _semiprime,
        _explain_semiprime,
        True,
    ),
    Property(
        "sphenic",
        "Sphenic",
        "A product of exactly three distinct primes.",
        (30, 42, 66, 70),
        _sphenic,
        _explain_sphenic,
        True,
    ),
)

ALIASES = {
    "square": "perfect_square",
    "cube": "perfect_cube",
    "palindrome": "palindromic",
    "narcissistic": "armstrong",
    "germain": "sophie_germain",
}

_BY_ID = {item.ident: item for item in REGISTRY}


def resolve(name: str) -> Property:
    """Return the property for a name or alias.

    Raises
    ------
    KeyError
        The name is not a known property or alias.
    """
    ident = ALIASES.get(name, name)
    try:
        return _BY_ID[ident]
    except KeyError:
        known = ", ".join(item.ident for item in REGISTRY)
        raise KeyError(known) from None


def evaluate(number: int, prop: Property, *, search: bool = False) -> tuple[Status, Facts]:
    """Check one property, factoring only when that property needs it."""
    facts = facts_for(number, search=search, factor=prop.needs_factors)
    return prop.check(facts), facts


def matching(
    number: int, *, search: bool = False
) -> tuple[list[tuple[Property, Facts]], list[str], Facts]:
    """Return matches, skipped identifiers, and the shared factorisation."""
    shared = facts_for(number, search=search, factor=True)
    plain = facts_for(number, search=search, factor=False)
    found: list[tuple[Property, Facts]] = []
    skipped: list[str] = []
    for prop in REGISTRY:
        facts = shared if prop.needs_factors else plain
        status = prop.check(facts)
        if status == "match":
            found.append((prop, facts))
        elif status == "skipped":
            skipped.append(prop.ident)
    return found, skipped, shared
