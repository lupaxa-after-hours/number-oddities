"""Extra recreational properties beyond the original eighteen.

A zero digit in a Munchhausen number contributes 0, so ``0 ** 0`` is 0.
That is what makes 438579088 work. Spy numbers need at least two digits,
so 0 through 9 are not included. Emirps are reversible primes that are
not palindromes. A hoax number uses each prime factor once; a Smith
number counts repeats.
"""

from __future__ import annotations

from lupaxa.number_oddities.analysis import Facts, cube_root, digit_sum, digits_of, factorise, is_cube, prime_status, proper_divisor_sum, square_root
from lupaxa.number_oddities.limits import TAXICAB_INSPECT_ROOT, TAXICAB_SEARCH_ROOT, VAMPIRE_INSPECT_DIGITS, VAMPIRE_SEARCH_DIGITS

_FACTORIALS = [1]
for _digit in range(1, 10):
    _FACTORIALS.append(_FACTORIALS[-1] * _digit)

_SUPERS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _times(left: int, right: int, *, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    return f"{left} {mark} {right}"


def _power(base: int, exponent: int, *, ascii_math: bool) -> str:
    if ascii_math:
        return f"{base}^{exponent}"
    return f"{base}{str(exponent).translate(_SUPERS)}"


def _factorion(facts: Facts) -> str:
    if facts.number < 0:
        return "miss"
    total = sum(_FACTORIALS[digit] for digit in facts.digits)
    return "match" if total == facts.number else "miss"


def _explain_factorion(facts: Facts, ascii_math: bool) -> str:
    terms = [f"{digit}!" for digit in facts.digits]
    values = [str(_FACTORIALS[digit]) for digit in facts.digits]
    lines = [" + ".join(terms)]
    if len(values) > 1:
        lines.append("= " + " + ".join(values))
    lines.append(f"= {facts.number}")
    return "\n".join(lines) + f"\n\n{facts.number} is a factorion."


def _dudeney(facts: Facts) -> str:
    if facts.number < 0 or not is_cube(facts.number):
        return "miss"
    return "match" if digit_sum(facts.number) == cube_root(facts.number) else "miss"


def _explain_dudeney(facts: Facts, ascii_math: bool) -> str:
    root = cube_root(facts.number)
    shown = _power(root, 3, ascii_math=ascii_math)
    parts = " + ".join(str(digit) for digit in facts.digits)
    return f"{shown} = {facts.number}\n{parts} = {root}\n\n{facts.number} is a Dudeney number."


def _keith(facts: Facts) -> str:
    return "match" if _keith_steps(facts.number) is not None else "miss"


def _keith_steps(number: int) -> list[int] | None:
    if number < 10:
        return None
    width = len(digits_of(number))
    series = list(digits_of(number))
    while series[-1] < number:
        series.append(sum(series[-width:]))
        if series[-1] == number:
            return series
    return None


def _explain_keith(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    series = _keith_steps(facts.number) or []
    shown = ", ".join(str(item) for item in series)
    return f"{shown}\n\n{facts.number} is a Keith number."


def _trimorphic(facts: Facts) -> str:
    if facts.number < 0:
        return "miss"
    return "match" if str(facts.number**3).endswith(str(facts.number)) else "miss"


def _explain_trimorphic(facts: Facts, ascii_math: bool) -> str:
    cube = facts.number**3
    shown = _power(facts.number, 3, ascii_math=ascii_math)
    return f"{shown} = {cube}\n{cube} ends with {facts.number}.\n\n{facts.number} is trimorphic."


def _zuckerman(facts: Facts) -> str:
    if facts.number <= 0 or 0 in facts.digits:
        return "miss"
    product = 1
    for digit in facts.digits:
        product *= digit
    return "match" if facts.number % product == 0 else "miss"


def _explain_zuckerman(facts: Facts, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    product = 1
    for digit in facts.digits:
        product *= digit
    shown = f" {mark} ".join(str(digit) for digit in facts.digits)
    divide = "/" if ascii_math else "÷"
    return f"{shown} = {product}\n{facts.number} {divide} {product} = {facts.number // product}\n\n{facts.number} is a Zuckerman number."


def _spy(facts: Facts) -> str:
    if facts.number < 0 or len(facts.digits) < 2:
        return "miss"
    product = 1
    for digit in facts.digits:
        product *= digit
    return "match" if product == sum(facts.digits) else "miss"


def _explain_spy(facts: Facts, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    parts = " + ".join(str(digit) for digit in facts.digits)
    shown = f" {mark} ".join(str(digit) for digit in facts.digits)
    total = sum(facts.digits)
    return f"{parts} = {total}\n{shown} = {total}\n\n{facts.number} is a spy number."


def _hoax(facts: Facts) -> str:
    if facts.number <= 1 or facts.factor_status != "complete":
        return "miss" if facts.number <= 1 else "skipped"
    if facts.factors == (facts.number,):
        return "miss"
    distinct: list[int] = []
    for factor in facts.factors:
        if factor not in distinct:
            distinct.append(factor)
    factor_digits = sum(digit_sum(factor) for factor in distinct)
    return "match" if factor_digits == sum(facts.digits) else "miss"


def _explain_hoax(facts: Facts, ascii_math: bool) -> str:
    distinct: list[int] = []
    for factor in facts.factors:
        if factor not in distinct:
            distinct.append(factor)
    mark = "*" if ascii_math else "×"
    shown = f" {mark} ".join(str(factor) for factor in distinct)
    number_digits = " + ".join(str(digit) for digit in facts.digits)
    factor_digits = " + ".join(str(digit) for factor in distinct for digit in digits_of(factor))
    return f"{facts.number} = {shown}\n{number_digits} = {sum(facts.digits)}\n{factor_digits} = {sum(digit_sum(factor) for factor in distinct)}\n\n{facts.number} is a hoax number."


def _amicable(facts: Facts) -> str:
    if facts.number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    partner = proper_divisor_sum(facts.number, facts.factors)
    if partner <= 1 or partner == facts.number:
        return "miss"
    status, factors = factorise(partner, search=facts.search)
    if status != "complete":
        return "skipped"
    return "match" if proper_divisor_sum(partner, factors) == facts.number else "miss"


def _explain_amicable(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    partner = proper_divisor_sum(facts.number, facts.factors)
    status, factors = factorise(partner, search=facts.search)
    back = proper_divisor_sum(partner, factors) if status == "complete" else facts.number
    return f"The proper divisors of {facts.number} sum to {partner}.\nThe proper divisors of {partner} sum to {back}.\n\n{facts.number} and {partner} are amicable."


def _vampire(facts: Facts) -> str:
    status, _fangs = _vampire_fangs(facts.number, search=facts.search)
    return status


def _vampire_fangs(number: int, *, search: bool) -> tuple[str, tuple[int, int]]:
    """Return the status and, for a match, the two fangs."""
    if number < 1000:
        return "miss", (0, 0)
    text = str(number)
    count = len(text)
    if count % 2:
        return "miss", (0, 0)
    limit = VAMPIRE_SEARCH_DIGITS if search else VAMPIRE_INSPECT_DIGITS
    if count > limit:
        return "skipped", (0, 0)
    half = count // 2
    low = 10 ** (half - 1)
    high = min(10**half - 1, square_root(number))
    target = sorted(text)
    for fang in range(low, high + 1):
        if number % fang:
            continue
        other = number // fang
        if other < fang:
            break
        other_text = str(other)
        if len(other_text) != half:
            continue
        if str(fang).endswith("0") and other_text.endswith("0"):
            continue
        if sorted(str(fang) + other_text) == target:
            return "match", (fang, other)
    return "miss", (0, 0)


def _explain_vampire(facts: Facts, ascii_math: bool) -> str:
    _status, fangs = _vampire_fangs(facts.number, search=False)
    shown = _times(fangs[0], fangs[1], ascii_math=ascii_math)
    return f"{facts.number} = {shown}\n\n{facts.number} is a vampire number."


def _taxicab(facts: Facts) -> str:
    status, _pairs = _taxicab_pairs(facts.number, search=facts.search)
    return status


def _taxicab_pairs(number: int, *, search: bool) -> tuple[str, list[tuple[int, int]]]:
    if number <= 1:
        return "miss", []
    cap = TAXICAB_SEARCH_ROOT if search else TAXICAB_INSPECT_ROOT
    pairs: list[tuple[int, int]] = []
    root = 1
    while root <= cap:
        cube = root * root * root
        if cube >= number:
            return ("match" if len(pairs) >= 2 else "miss"), pairs
        rest = number - cube
        other = cube_root(rest)
        if other > root and other * other * other == rest:
            pairs.append((root, other))
        root += 1
    return "skipped", pairs


def _explain_taxicab(facts: Facts, ascii_math: bool) -> str:
    _status, pairs = _taxicab_pairs(facts.number, search=False)
    lines = []
    for left, right in pairs:
        lines.append(f"{_power(left, 3, ascii_math=ascii_math)} + {_power(right, 3, ascii_math=ascii_math)} = {facts.number}")
    return "\n".join(lines) + f"\n\n{facts.number} is a taxicab number."


def _emirp(facts: Facts) -> str:
    number = facts.number
    if number < 10:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    if facts.factors != (number,):
        return "miss"
    text = str(number)
    if text == text[::-1]:
        return "miss"
    return prime_status(int(text[::-1]), search=facts.search)


def _explain_emirp(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    reverse = int(str(facts.number)[::-1])
    return f"{facts.number} reversed is {reverse}. Both are prime.\n\n{facts.number} is an emirp."


def _munchhausen(facts: Facts) -> str:
    if facts.number <= 0:
        return "miss"
    total = 0
    for digit in facts.digits:
        total += 0 if digit == 0 else digit**digit
    return "match" if total == facts.number else "miss"


def _explain_munchhausen(facts: Facts, ascii_math: bool) -> str:
    terms = []
    values = []
    for digit in facts.digits:
        terms.append(_power(digit, digit, ascii_math=ascii_math))
        values.append(0 if digit == 0 else digit**digit)
    lines = [" + ".join(terms)]
    if len(values) > 1:
        lines.append("= " + " + ".join(str(value) for value in values))
    lines.append(f"= {sum(values)}")
    return "\n".join(lines) + f"\n\n{facts.number} is a Munchhausen number."


def _lucas_index(number: int) -> int | None:
    if number < 1:
        return None
    previous, current = 2, 1
    if number == 2:
        return 0
    index = 1
    while current < number:
        previous, current = current, previous + current
        index += 1
    return index if current == number else None


def _lucas(facts: Facts) -> str:
    return "match" if _lucas_index(facts.number) is not None else "miss"


def _explain_lucas(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    index = _lucas_index(facts.number)
    return f"L({index}) = {facts.number}\n\n{facts.number} is a Lucas number."


def _catalan_index(number: int) -> int | None:
    if number < 1:
        return None
    value = 1
    index = 0
    while value < number:
        index += 1
        value = value * (4 * index - 2) // (index + 1)
    return index if value == number else None


def _catalan(facts: Facts) -> str:
    return "match" if _catalan_index(facts.number) is not None else "miss"


def _explain_catalan(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    index = _catalan_index(facts.number)
    return f"C({index}) = {facts.number}\n\n{facts.number} is a Catalan number."


def _pell_index(number: int) -> int | None:
    if number < 0:
        return None
    previous, current = 0, 1
    if number == 0:
        return 0
    index = 1
    while current < number:
        previous, current = current, 2 * current + previous
        index += 1
    return index if current == number else None


def _pell(facts: Facts) -> str:
    return "match" if _pell_index(facts.number) is not None else "miss"


def _explain_pell(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    index = _pell_index(facts.number)
    return f"P({index}) = {facts.number}\n\n{facts.number} is a Pell number."


def _factorial_index(number: int) -> int | None:
    if number < 1:
        return None
    value = 1
    index = 0
    while value < number:
        index += 1
        value *= index
    return index if value == number else None


def _factorial(facts: Facts) -> str:
    return "match" if _factorial_index(facts.number) is not None else "miss"


def _explain_factorial(facts: Facts, ascii_math: bool) -> str:
    del ascii_math
    index = _factorial_index(facts.number)
    return f"{index}! = {facts.number}\n\n{facts.number} is a factorial number."


def _primorial_primes(number: int) -> list[int] | None:
    if number < 2:
        return None
    primes: list[int] = []
    product = 1
    candidate = 2
    while product < number:
        if prime_status(candidate) == "match":
            primes.append(candidate)
            product *= candidate
        candidate += 1 if candidate == 2 else 2
    return primes if product == number else None


def _primorial(facts: Facts) -> str:
    return "match" if _primorial_primes(facts.number) is not None else "miss"


def _explain_primorial(facts: Facts, ascii_math: bool) -> str:
    primes = _primorial_primes(facts.number) or []
    mark = "*" if ascii_math else "×"
    shown = f" {mark} ".join(str(prime) for prime in primes)
    return f"{shown} = {facts.number}\n\n{facts.number} is a primorial."


def _sophie(facts: Facts) -> str:
    number = facts.number
    if number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    if facts.factors != (number,):
        return "miss"
    return prime_status(2 * number + 1, search=facts.search)


def _explain_sophie(facts: Facts, ascii_math: bool) -> str:
    safe = 2 * facts.number + 1
    shown = _times(2, facts.number, ascii_math=ascii_math)
    return f"{facts.number} is prime, and {shown} + 1 = {safe} is prime.\n\n{facts.number} is a Sophie Germain prime."


def _semiprime(facts: Facts) -> str:
    if facts.number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    return "match" if len(facts.factors) == 2 else "miss"


def _explain_semiprime(facts: Facts, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    shown = f" {mark} ".join(str(factor) for factor in facts.factors)
    return f"{facts.number} = {shown}\n\n{facts.number} is a semiprime."


def _sphenic(facts: Facts) -> str:
    if facts.number <= 1:
        return "miss"
    if facts.factor_status != "complete":
        return "skipped"
    return "match" if len(facts.factors) == 3 and len(set(facts.factors)) == 3 else "miss"


def _explain_sphenic(facts: Facts, ascii_math: bool) -> str:
    mark = "*" if ascii_math else "×"
    shown = f" {mark} ".join(str(factor) for factor in facts.factors)
    return f"{facts.number} = {shown}\n\n{facts.number} is a sphenic number."
