"""Known examples and the boundaries between similar properties."""

from __future__ import annotations

import pytest

from lupaxa.number_oddities.properties import REGISTRY, evaluate, matching, resolve

CASES = {
    "prime": ([2, 3, 5], [1, 4, 9, 0, -2]),
    "composite": ([4, 6, 9], [1, 2, 3, 0, -4]),
    "perfect": ([6, 28, 496], [1, 12, 10, 0, -6]),
    "abundant": ([12, 18, 20], [1, 2, 6, 28]),
    "deficient": ([1, 2, 8], [6, 12, 28, 0, -1]),
    "perfect_square": ([0, 1, 36], [2, 3, 8, -4]),
    "perfect_cube": ([0, 1, -8, 8], [2, 4, -2]),
    "triangular": ([0, 1, 36], [2, 4, -1]),
    "pronic": ([0, 2, 6], [1, 3, 4, -2]),
    "fibonacci": ([0, 1, 2, 8], [4, 6, -1]),
    "palindromic": ([0, 1, 121], [10, 12, -121]),
    "automorphic": ([0, 1, 25], [2, 4, -1]),
    "harshad": ([1, 24, 153], [0, 13, -18]),
    "armstrong": ([0, 1, 153, 370], [135, 22, -153]),
    "disarium": ([0, 1, 135, 175], [153, 22, -135]),
    "kaprekar": ([1, 9, 45], [0, 10, 46, -45]),
    "happy": ([1, 7, 19], [0, 2, 4, -7]),
    "smith": ([4, 22, 666], [2, 3, 1, 0, 153]),
    "factorion": ([1, 2, 145, 40585], [0, 24, 146, -1]),
    "dudeney": ([0, 1, 512, 4913], [8, 27, 64, -512]),
    "keith": ([14, 19, 28, 47], [10, 11, 12, 13]),
    "trimorphic": ([0, 1, 25, 76], [2, 3, 7, -1]),
    "zuckerman": ([11, 12, 24, 135], [0, 10, 23, -24]),
    "spy": ([22, 123, 1124], [7, 10, 12, 13]),
    "hoax": ([22, 58, 84, 94], [1, 2, 4, 27]),
    "amicable": ([220, 284, 1184], [1, 6, 12, 28]),
    "vampire": ([1260, 1395, 1435], [21, 1000, 1261]),
    "taxicab": ([1729, 4104, 13832], [0, 2, 91, 1728]),
    "emirp": ([13, 17, 31, 37], [2, 10, 11, 15]),
    "munchhausen": ([1, 3435, 438579088], [0, 2, 3434, -1]),
    "lucas": ([1, 2, 4, 7], [0, 5, 6, 8]),
    "catalan": ([1, 2, 5, 14], [0, 3, 4, 6]),
    "pell": ([0, 1, 2, 5], [3, 4, 6, -1]),
    "factorial": ([1, 2, 6, 24], [0, 3, 4, 5]),
    "primorial": ([2, 6, 30, 210], [0, 1, 4, 12]),
    "sophie_germain": ([2, 3, 5, 11], [1, 7, 13, 17]),
    "semiprime": ([4, 6, 9, 15], [1, 2, 8, 12, 30]),
    "sphenic": ([30, 42, 66, 70], [4, 6, 12, 210]),
}


@pytest.mark.parametrize("ident", [item.ident for item in REGISTRY])
def test_examples_match_and_counterexamples_do_not(ident: str) -> None:
    """Each property accepts its known examples and rejects the nearby numbers."""
    prop = resolve(ident)
    matches, misses = CASES[ident]
    assert len(matches) >= 3
    assert len(misses) >= 3
    for number in matches:
        status, _facts = evaluate(number, prop)
        assert status == "match", number
    for number in misses:
        status, _facts = evaluate(number, prop)
        assert status == "miss", number


def test_registry_has_thirty_eight_properties() -> None:
    """The catalogue publishes thirty-eight stable identifiers."""
    assert len(REGISTRY) == 38
    assert len({item.ident for item in REGISTRY}) == 38


def test_aliases() -> None:
    """Common names resolve to the stable identifiers."""
    assert resolve("square").ident == "perfect_square"
    assert resolve("cube").ident == "perfect_cube"
    assert resolve("palindrome").ident == "palindromic"
    assert resolve("narcissistic").ident == "armstrong"
    assert resolve("germain").ident == "sophie_germain"


def test_spec_fixtures() -> None:
    """The numbers called out in the specification keep their classifications."""
    assert _ids(2) >= {"prime"}
    assert "prime" not in _ids(1)
    assert "composite" not in _ids(1)
    assert "perfect" in _ids(28)
    assert {"armstrong", "harshad"} <= _ids(153)
    assert "happy" in _ids(19)
    assert "automorphic" in _ids(25)
    assert "kaprekar" in _ids(45)
    assert "smith" in _ids(666)
    assert "disarium" in _ids(135)
    assert {"perfect_square", "triangular"} <= _ids(36)
    assert {"perfect_square", "perfect_cube", "fibonacci", "triangular", "pronic"} <= _ids(0)
    assert "perfect_cube" in _ids(-8)
    assert _ids(-8) == {"perfect_cube"}


def test_similar_properties_stay_distinct() -> None:
    """Numbers that share one label do not inherit the neighbouring label."""
    assert "perfect_cube" not in _ids(36)
    assert "perfect" not in _ids(12)
    assert "abundant" not in _ids(28)
    assert "disarium" not in _ids(153)
    assert "armstrong" not in _ids(135)
    assert "prime" not in _ids(4)
    assert "smith" in _ids(4)
    assert "hoax" not in _ids(4)
    assert "hoax" not in _ids(27)
    assert "hoax" in _ids(22)
    assert "emirp" not in _ids(11)
    assert "semiprime" not in _ids(30)
    assert "sphenic" in _ids(30)
    assert "sphenic" not in _ids(12)


def test_explanations_show_the_working() -> None:
    """A match explains the arithmetic instead of only naming the property."""
    prop = resolve("disarium")
    status, facts = evaluate(135, prop)
    assert status == "match"
    text = prop.explain(facts, False)
    assert "1¹ + 3² + 5³" in text
    assert "= 1 + 9 + 125" in text
    assert "= 135" in text
    ascii_text = prop.explain(facts, True)
    assert "1^1 + 3^2 + 5^3" in ascii_text
    single, single_facts = evaluate(2, prop)
    assert single == "match"
    single_lines = prop.explain(single_facts, False).splitlines()
    assert single_lines.count("= 2") == 1


def test_expensive_checks_skip_during_search() -> None:
    """Range search does not walk huge fang or cube-root loops."""
    huge = 10**7
    status, _facts = evaluate(huge, resolve("vampire"), search=True)
    assert status == "skipped"
    status, _facts = evaluate(10**12 + 1, resolve("taxicab"), search=True)
    assert status == "skipped"


def test_large_number_is_skipped_rather_than_called_composite() -> None:
    """An unfinished factorisation is not reported as a negative result."""
    status, _facts = evaluate(10**18 + 3, resolve("prime"), search=True)
    assert status == "skipped"
    status, _facts = evaluate(10**18 + 3, resolve("composite"), search=True)
    assert status == "skipped"


def _ids(number: int) -> set[str]:
    found, skipped, _shared = matching(number)
    assert not skipped
    return {prop.ident for prop, _facts in found}
