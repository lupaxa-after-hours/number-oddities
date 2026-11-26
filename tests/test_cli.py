"""Command behaviour, exit codes, and structured output."""

from __future__ import annotations

import json

import pytest

from lupaxa.number_oddities.cli import main
from lupaxa.number_oddities.properties import evaluate, resolve


def test_shorthand_and_inspect_agree(capsys: pytest.CaptureFixture[str]) -> None:
    """The bare number and the inspect command describe the same integer."""
    assert main(["135"]) == 0
    shorthand = capsys.readouterr().out
    assert main(["inspect", "135"]) == 0
    explicit = capsys.readouterr().out
    assert shorthand == explicit
    assert "Disarium" in explicit
    assert "135" in explicit


def test_properties_and_explain() -> None:
    """The catalogue lists every property, and explain works through an alias."""
    assert main(["properties", "--format", "json"]) == 0
    assert main(["explain", "narcissistic"]) == 0


def test_properties_json(capsys: pytest.CaptureFixture[str]) -> None:
    """Property JSON is a list of the thirty-eight identifiers."""
    assert main(["--format", "json", "properties"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 38
    assert payload[0]["id"] == "prime"


def test_find_is_ordered_and_limited(capsys: pytest.CaptureFixture[str]) -> None:
    """Search results ascend, and limit stops after the requested matches."""
    assert main(["find", "prime", "--start", "0", "--end", "20", "--limit", "3"]) == 0
    text = capsys.readouterr().out
    assert _listed_numbers(text) == [2, 3, 5]


def test_count_only_is_the_full_count(capsys: pytest.CaptureFixture[str]) -> None:
    """Count-only reports every match in the range, not a limited sample."""
    assert main(["find", "square", "--start", "0", "--end", "10", "--count-only", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 4
    assert "matches" not in payload


def test_compare_matches_inspection(capsys: pytest.CaptureFixture[str]) -> None:
    """Shared properties are the intersection of the two inspections."""
    assert main(["compare", "153", "370", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    left = set(payload["numbers"][0]["properties"])
    right = set(payload["numbers"][1]["properties"])
    assert set(payload["shared"]) == left & right
    assert "armstrong" in payload["shared"]


def test_random_qualifies(capsys: pytest.CaptureFixture[str]) -> None:
    """A seeded discovery returns a number that has the reported property."""
    assert (
        main(
            [
                "random",
                "--property",
                "prime",
                "--start",
                "10",
                "--end",
                "40",
                "--seed",
                "1",
                "--format",
                "json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    status, _facts = evaluate(payload["number"], resolve("prime"))
    assert status == "match"
    assert 10 <= payload["number"] <= 40


def test_random_without_property_still_qualifies(capsys: pytest.CaptureFixture[str]) -> None:
    """An unspecified discovery still names a property the number satisfies."""
    assert main(["random", "--seed", "3", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    status, _facts = evaluate(payload["number"], resolve(payload["property"]))
    assert status == "match"


def test_no_matches_is_success(capsys: pytest.CaptureFixture[str]) -> None:
    """A search with no matches exits 0 and reports a zero count."""
    assert main(["find", "perfect", "--start", "7", "--end", "10", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 0
    assert payload["matches"] == []


def test_no_random_candidate(capsys: pytest.CaptureFixture[str]) -> None:
    """Random discovery says so when the range has no qualifying integer."""
    assert main(["random", "--start", "-3", "--end", "-2"]) == 0
    assert "No qualifying number" in capsys.readouterr().out


def test_exit_codes(capsys: pytest.CaptureFixture[str]) -> None:
    """Invalid input uses exit 2, and an oversized range uses exit 3."""
    assert main([]) == 2
    assert "usage:" in capsys.readouterr().err
    assert main(["inspect"]) == 2
    assert "number" in capsys.readouterr().err
    assert main(["inspect", "nope"]) == 2
    assert "integer" in capsys.readouterr().err
    assert main(["explain", "magic"]) == 2
    err = capsys.readouterr().err
    assert "prime" in err
    assert main(["find", "prime", "--start", "5", "--end", "1"]) == 2
    assert "start" in capsys.readouterr().err
    assert main(["find", "prime", "--start", "0", "--end", "100000"]) == 3
    assert "100000" in capsys.readouterr().err
    assert main(["--format", "yaml", "properties"]) == 2
    assert "text or json" in capsys.readouterr().err
    assert main(["--help"]) == 0
    assert main(["--version"]) == 0


def test_json_inspection_parses(capsys: pytest.CaptureFixture[str]) -> None:
    """Inspection JSON contains the basic facts and the matching explanation."""
    assert main(["--format", "json", "inspect", "28"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["number"] == 28
    assert payload["basic"]["factors_status"] == "complete"
    assert "perfect" in {item["id"] for item in payload["matches"]}


def test_text_layout_is_a_table(capsys: pytest.CaptureFixture[str]) -> None:
    """Text results line up in tables, and --ascii keeps the same columns."""
    assert main(["135"]) == 0
    text = capsys.readouterr().out
    assert "│ Number" in text
    assert "│ Disarium" in text
    assert "Explanation" in text
    assert "is composite." not in text
    assert "is a Disarium number." not in text
    assert main(["--ascii", "135"]) == 0
    plain = capsys.readouterr().out
    assert plain.startswith("+")
    assert "×" not in plain
    assert "*" in plain


def _listed_numbers(text: str) -> list[int]:
    found: list[int] = []
    for line in text.splitlines():
        cell = line.replace("│", "|").strip("| ").strip()
        if cell.isdigit():
            found.append(int(cell))
    return found
