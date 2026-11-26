"""Text and JSON rendering. JSON is the only thing written for ``--format json``."""

from __future__ import annotations

import json
import re
import sys
from typing import TextIO

from lupaxa.number_oddities.analysis import Facts, digit_sum, parity_of, sign_of
from lupaxa.number_oddities.properties import Property, evaluate

_RESET = "\033[0m"
_BOLD = "\033[1m"
_BOX = {
    "tl": "┌",
    "tr": "┐",
    "bl": "└",
    "br": "┘",
    "h": "─",
    "v": "│",
    "lj": "├",
    "rj": "┤",
    "tj": "┬",
    "bj": "┴",
    "x": "┼",
}
_ASCII_BOX = {
    "tl": "+",
    "tr": "+",
    "bl": "+",
    "br": "+",
    "h": "-",
    "v": "|",
    "lj": "+",
    "rj": "+",
    "tj": "+",
    "bj": "+",
    "x": "+",
}


def use_colour(enabled: bool, stream: TextIO) -> bool:
    """Return whether text labels should be coloured."""
    return enabled and stream.isatty()


def _label(text: str, colour: bool) -> str:
    if not colour:
        return text
    return f"{_BOLD}{text}{_RESET}"


def _glyphs(ascii_rules: bool) -> dict[str, str]:
    return _ASCII_BOX if ascii_rules else _BOX


_CLOSING = re.compile(r"^-?\d+ is (?:a |an )?.+\.$|^-?\d+ and -?\d+ are amicable\.$")


def _compact(text: str) -> str:
    """Keep the arithmetic and drop the sentence that only names the property."""
    parts = text.split("\n\n")
    if len(parts) > 1 and _CLOSING.match(parts[-1].strip()):
        parts = parts[:-1]
    lines = [line for part in parts for line in part.split("\n") if line]
    if len(lines) == 1:
        lines[0] = re.sub(r"^-?\d+ is prime\. ", "", lines[0])
    return "\n".join(lines)


def _wrap(text: str, width: int | None) -> list[str]:
    """Split a cell on newlines, and wrap long lines on spaces."""
    raw = text.split("\n")
    if width is None:
        return raw or [""]
    lines: list[str] = []
    for paragraph in raw:
        if paragraph == "":
            lines.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
            if current and len(current) + 1 + len(word) > width:
                lines.append(current)
                current = word
            elif current:
                current = f"{current} {word}"
            else:
                current = word
        lines.append(current)
    return lines or [""]


def _pad(text: str, width: int, align: str) -> str:
    if align == "right":
        return text.rjust(width)
    if align == "center":
        return text.center(width)
    return text.ljust(width)


def _rule(kind: str, widths: list[int], glyphs: dict[str, str]) -> str:
    edges = {"top": ("tl", "tj", "tr"), "mid": ("lj", "x", "rj"), "bottom": ("bl", "bj", "br")}
    left, join, right = edges[kind]
    parts = [glyphs["h"] * (width + 2) for width in widths]
    return glyphs[left] + glyphs[join].join(parts) + glyphs[right]


def _table(
    rows: list[list[str]],
    *,
    ascii_rules: bool,
    colour: bool,
    header: bool = False,
    aligns: list[str] | None = None,
    wrap: list[int | None] | None = None,
    separate: bool = False,
    bold_keys: bool = False,
) -> str:
    """Render one aligned text table. JSON callers do not use this."""
    glyphs = _glyphs(ascii_rules)
    columns = len(rows[0])
    limits = wrap or [None] * columns
    placed = aligns or ["left"] * columns
    wrapped = [[_wrap(cell, limit) for cell, limit in zip(row, limits, strict=True)] for row in rows]
    widths = [1] * columns
    for row in wrapped:
        for index, lines in enumerate(row):
            widths[index] = max(widths[index], *(len(line) for line in lines))
    drawn: list[str] = [_rule("top", widths, glyphs)]
    for row_index, row in enumerate(wrapped):
        height = max(len(lines) for lines in row)
        for line_index in range(height):
            cells: list[str] = []
            for index, lines in enumerate(row):
                text = lines[line_index] if line_index < len(lines) else ""
                padded = _pad(text, widths[index], placed[index])
                bold = colour and (row_index == 0 if header else bold_keys and index == 0)
                cells.append(_label(padded, bold))
            body = f" {glyphs['v']} ".join(cells)
            drawn.append(f"{glyphs['v']} {body} {glyphs['v']}")
        more = row_index + 1 < len(wrapped)
        under_header = header and row_index == 0
        between = (separate and row_index > 0) if header else separate
        if more and (under_header or between):
            drawn.append(_rule("mid", widths, glyphs))
    drawn.append(_rule("bottom", widths, glyphs))
    return "\n".join(drawn)


def render_inspection(
    facts: Facts,
    matches: list[tuple[Property, Facts]],
    skipped: list[str],
    *,
    output_format: str,
    colour: bool,
    ascii_math: bool,
) -> str:
    """Render one inspection."""
    if output_format == "json":
        return json.dumps(_inspection_json(facts, matches, skipped, ascii_math=False), indent=2)
    return _inspection_text(facts, matches, skipped, colour=colour, ascii_math=ascii_math)


def _inspection_json(
    facts: Facts,
    matches: list[tuple[Property, Facts]],
    skipped: list[str],
    *,
    ascii_math: bool,
) -> dict[str, object]:
    return {
        "number": facts.number,
        "basic": _basic(facts),
        "matches": [
            {
                "id": _ident(prop),
                "name": _title(prop),
                "explanation": _explain(prop, item, ascii_math),
            }
            for prop, item in matches
        ],
        "skipped": skipped,
    }


def _inspection_text(
    facts: Facts,
    matches: list[tuple[Property, Facts]],
    skipped: list[str],
    *,
    colour: bool,
    ascii_math: bool,
) -> str:
    basic = _basic(facts)
    blocks = [
        _table(
            [
                ["Number", str(facts.number)],
                ["Sign", str(basic["sign"])],
                ["Digits", str(basic["digits"])],
                ["Digit sum", str(basic["digit_sum"])],
                ["Parity", str(basic["parity"])],
                ["Factors", _factor_text(facts, ascii_math)],
            ],
            ascii_rules=ascii_math,
            colour=colour,
            bold_keys=True,
            wrap=[None, 64],
        )
    ]
    if matches:
        match_rows = [["Property", "Explanation"]]
        for prop, item in matches:
            match_rows.append([_title(prop), _compact(_explain(prop, item, ascii_math))])
        blocks.append(
            _table(
                match_rows,
                ascii_rules=ascii_math,
                colour=colour,
                header=True,
                separate=True,
                wrap=[None, 64],
            )
        )
    else:
        blocks.append(_table([["Matches", "none"]], ascii_rules=ascii_math, colour=colour, bold_keys=True))
    if skipped:
        blocks.append(
            _table(
                [["Skipped", ", ".join(skipped)]],
                ascii_rules=ascii_math,
                colour=colour,
                bold_keys=True,
                wrap=[None, 64],
            )
        )
    return "\n\n".join(blocks)


def _basic(facts: Facts) -> dict[str, object]:
    return {
        "sign": sign_of(facts.number),
        "absolute": abs(facts.number),
        "digits": len(facts.digits),
        "digit_sum": digit_sum(facts.number),
        "parity": parity_of(facts.number),
        "factors": list(facts.factors),
        "factors_status": facts.factor_status,
    }


def _factor_text(facts: Facts, ascii_math: bool) -> str:
    if facts.factor_status == "skipped":
        return "skipped"
    if not facts.factors:
        return "none"
    mark = "*" if ascii_math else "×"
    return f" {mark} ".join(str(factor) for factor in facts.factors)


def _ident(prop: Property) -> str:
    return prop.ident


def _title(prop: Property) -> str:
    return prop.title


def _explain(prop: Property, facts: Facts, ascii_math: bool) -> str:
    return prop.explain(facts, ascii_math)


def render_properties(output_format: str, *, ascii_math: bool = False, colour: bool = False) -> str:
    """Render the property catalogue."""
    from lupaxa.number_oddities.properties import REGISTRY

    if output_format == "json":
        payload = [{"id": item.ident, "name": item.title, "description": item.description} for item in REGISTRY]
        return json.dumps(payload, indent=2)
    rows = [["Identifier", "Name", "Meaning"]]
    rows.extend([item.ident, item.title, item.description] for item in REGISTRY)
    return _table(
        rows,
        ascii_rules=ascii_math,
        colour=colour,
        header=True,
        wrap=[None, None, 52],
    )


def render_explanation(prop: Property, *, output_format: str, ascii_math: bool, colour: bool = False) -> str:
    """Render a property definition and one worked example."""
    example = prop.examples[0]
    _status, facts = evaluate(example, prop)
    body = _explain(prop, facts, ascii_math)
    if output_format == "json":
        return json.dumps(
            {
                "id": _ident(prop),
                "name": _title(prop),
                "description": prop.description,
                "example": example,
                "explanation": _explain(prop, facts, False),
            },
            indent=2,
        )
    return _table(
        [
            ["Property", _title(prop)],
            ["Description", prop.description],
            ["Example", str(example)],
            ["Explanation", _compact(body)],
        ],
        ascii_rules=ascii_math,
        colour=colour,
        bold_keys=True,
        separate=True,
        wrap=[None, 64],
    )


def render_find(
    prop: Property,
    start: int,
    end: int,
    matches: list[int],
    *,
    count_only: bool,
    output_format: str,
    ascii_math: bool = False,
    colour: bool = False,
) -> str:
    """Render a range search."""
    count = len(matches)
    if output_format == "json":
        payload: dict[str, object] = {
            "property": _ident(prop),
            "start": start,
            "end": end,
            "count": count,
        }
        if not count_only:
            payload["matches"] = matches
        return json.dumps(payload, indent=2)
    blocks = [
        _table(
            [
                ["Property", _title(prop)],
                ["Range", f"{start} to {end}"],
                ["Matches", str(count)],
            ],
            ascii_rules=ascii_math,
            colour=colour,
            bold_keys=True,
        )
    ]
    if not count_only and matches:
        blocks.append(
            _table(
                [["Value"], *[[str(number)] for number in matches]],
                ascii_rules=ascii_math,
                colour=colour,
                header=True,
                aligns=["right"],
            )
        )
    return "\n\n".join(blocks)


def render_compare(
    numbers: list[int],
    rows: list[list[str]],
    *,
    output_format: str,
    ascii_math: bool = False,
    colour: bool = False,
) -> str:
    """Render a comparison of two or more integers."""
    shared = sorted(set(rows[0]).intersection(*rows[1:])) if rows else []
    if output_format == "json":
        return json.dumps(
            {
                "numbers": [{"number": number, "properties": props} for number, props in zip(numbers, rows, strict=True)],
                "shared": shared,
            },
            indent=2,
        )
    from lupaxa.number_oddities.properties import REGISTRY

    owned = [set(props) for props in rows]
    present = set.union(*owned) if owned else set()
    shown = [item for item in REGISTRY if item.ident in present]
    header = ["Property", *[str(number) for number in numbers]]
    body = [[item.title, *["yes" if item.ident in have else "" for have in owned]] for item in shown]
    shared_names = [item.title for item in shown if item.ident in set(shared)]
    grid = _table(
        [header, *body] if body else [header, ["none", *[""] * len(numbers)]],
        ascii_rules=ascii_math,
        colour=colour,
        header=True,
        aligns=["left", *["center"] * len(numbers)],
    )
    shared_row = _table(
        [["Shared", ", ".join(shared_names) if shared_names else "none"]],
        ascii_rules=ascii_math,
        colour=colour,
        bold_keys=True,
        wrap=[None, 64],
    )
    return f"{grid}\n\n{shared_row}"


def render_random(
    number: int | None,
    prop: Property | None,
    *,
    output_format: str,
    colour: bool,
    ascii_math: bool,
) -> str:
    """Render a discovered number, or the message that none exists."""
    if number is None or prop is None:
        message = "No qualifying number exists within the selected bounds."
        if output_format == "json":
            return json.dumps({"number": None, "property": None, "message": message}, indent=2)
        return message
    _status, facts = evaluate(number, prop)
    if output_format == "json":
        return json.dumps(
            {
                "number": number,
                "property": _ident(prop),
                "explanation": _explain(prop, facts, False),
            },
            indent=2,
        )
    return _table(
        [
            ["Number", str(number)],
            ["Property", _title(prop)],
            ["Explanation", _compact(_explain(prop, facts, ascii_math))],
        ],
        ascii_rules=ascii_math,
        colour=colour,
        bold_keys=True,
        separate=True,
        wrap=[None, 64],
    )


def write_stdout(text: str) -> None:
    """Print text, treating a closed pipe as success."""
    try:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    except BrokenPipeError:
        raise SystemExit(0) from None
