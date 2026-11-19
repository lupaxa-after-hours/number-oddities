"""Argument parsing and command dispatch for ``number-oddities``."""

from __future__ import annotations

import os
import re
import sys
from random import Random

from lupaxa.number_oddities.analysis import find_numbers, inspect_number
from lupaxa.number_oddities.limits import MAX_RANGE
from lupaxa.number_oddities.output import (
    render_compare,
    render_explanation,
    render_find,
    render_inspection,
    render_properties,
    render_random,
    use_colour,
    write_stdout,
)
from lupaxa.number_oddities.properties import REGISTRY, Property, resolve
from lupaxa.number_oddities.version import __version__

_INTEGER = re.compile(r"[+-]?[0-9]+(?:_[0-9]+)*")
_COMMANDS = ("inspect", "properties", "explain", "find", "compare", "random")

_USAGE = """\
usage: number-oddities [--format text|json] [--no-color] [--ascii] [--verbose]
                      <number>
       number-oddities inspect <number>
       number-oddities properties
       number-oddities explain <property>
       number-oddities find <property> [--start N] [--end N] [--limit N] [--count-only]
       number-oddities compare <number> <number>...
       number-oddities random [--property NAME] [--start N] [--end N] [--seed N]

Inspect integers for recreational properties. Nothing is downloaded or stored.
"""


class UsageError(Exception):
    """Invalid arguments or a request past a safety limit."""

    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def main(argv: list[str] | None = None) -> int:
    """Run one command. Ordinary input errors do not print a traceback."""
    args = list(sys.argv[1:] if argv is None else argv)
    verbose = "--verbose" in args
    try:
        return _dispatch(args)
    except UsageError as exc:
        print(exc, file=sys.stderr)
        return exc.code
    except BrokenPipeError:
        return 0
    except Exception as exc:
        if verbose:
            raise
        print(f"number-oddities: {exc}", file=sys.stderr)
        return 1


def _dispatch(args: list[str]) -> int:
    options, rest = _globals(args)
    if options["version"]:
        print(f"number-oddities {__version__}")
        return 0
    if not rest or rest in (["--help"], ["-h"]):
        if rest:
            print(_USAGE, end="")
            return 0
        print(_USAGE, end="", file=sys.stderr)
        return 2
    command, payload = _command(rest)
    if payload[:1] in (["--help"], ["-h"]):
        print(_USAGE, end="")
        return 0
    output_format = str(options["format"])
    colour = use_colour(bool(options["colour"]), sys.stdout) and output_format == "text"
    ascii_math = bool(options["ascii"])
    if command == "properties":
        _reject_unknown(payload)
        write_stdout(render_properties(output_format, ascii_math=ascii_math, colour=colour))
        return 0
    if command == "explain":
        name = _one(payload, "a property name is required")
        write_stdout(
            render_explanation(
                _named(name), output_format=output_format, ascii_math=ascii_math, colour=colour
            )
        )
        return 0
    if command == "inspect":
        number = _integer(_one(payload, "a number is required"))
        facts, matches, skipped = inspect_number(number)
        _verbose(options, f"inspected {number}; matches={len(matches)}; skipped={len(skipped)}")
        write_stdout(
            render_inspection(
                facts,
                matches,
                skipped,
                output_format=output_format,
                colour=colour,
                ascii_math=ascii_math,
            )
        )
        return 0
    if command == "find":
        return _find(payload, options, output_format, ascii_math, colour)
    if command == "compare":
        return _compare(payload, output_format, ascii_math, colour)
    if command == "random":
        return _random(payload, options, output_format, ascii_math, colour)
    raise UsageError(_USAGE.strip())


def _find(
    payload: list[str],
    options: dict[str, object],
    output_format: str,
    ascii_math: bool,
    colour: bool,
) -> int:
    if not payload:
        raise UsageError("a property name is required")
    prop = _named(payload[0])
    start, end, limit, count_only = _find_options(payload[1:])
    _check_range(start, end)
    found = find_numbers(prop, start, end, limit=None if count_only else limit)
    _verbose(options, f"searched {end - start + 1} integers from {start} to {end}")
    write_stdout(
        render_find(
            prop,
            start,
            end,
            found,
            count_only=count_only,
            output_format=output_format,
            ascii_math=ascii_math,
            colour=colour,
        )
    )
    return 0


def _compare(payload: list[str], output_format: str, ascii_math: bool, colour: bool) -> int:
    if len(payload) < 2:
        raise UsageError("compare requires at least two integers")
    numbers = [_integer(arg) for arg in payload]
    rows: list[list[str]] = []
    for number in numbers:
        _facts, matches, _skipped = inspect_number(number)
        rows.append([item.ident for item, _facts in matches])
    write_stdout(
        render_compare(
            numbers, rows, output_format=output_format, ascii_math=ascii_math, colour=colour
        )
    )
    return 0


def _random(
    payload: list[str],
    options: dict[str, object],
    output_format: str,
    ascii_math: bool,
    colour: bool,
) -> int:
    start, end, prop, seed = _random_options(payload)
    _check_range(start, end)
    number, chosen = _discover(start, end, prop, seed)
    write_stdout(
        render_random(
            number,
            chosen,
            output_format=output_format,
            colour=colour,
            ascii_math=ascii_math,
        )
    )
    _verbose(options, f"random search from {start} to {end}")
    return 0


def _discover(
    start: int, end: int, prop: Property | None, seed: int | None
) -> tuple[int | None, Property | None]:
    rng = Random(seed) if seed is not None else Random()
    if prop is not None:
        groups = [[prop]]
    else:
        groups = [
            [item for item in REGISTRY if item.ident not in {"deficient", "composite"}],
            [item for item in REGISTRY if item.ident in {"deficient", "composite"}],
        ]
    for group in groups:
        order = list(group)
        rng.shuffle(order)
        for item in order:
            hits = find_numbers(item, start, end, limit=None)
            if hits:
                return rng.choice(hits), item
    return None, None


def _globals(args: list[str]) -> tuple[dict[str, object], list[str]]:
    options: dict[str, object] = {
        "format": "text",
        "colour": not os.environ.get("NO_COLOR"),
        "verbose": False,
        "ascii": False,
        "version": False,
    }
    rest: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            rest.extend(args[index + 1 :])
            break
        if arg == "--format":
            options["format"] = _format(_next(args, index, "format must be text or json"))
            index += 2
            continue
        if arg.startswith("--format="):
            options["format"] = _format(arg.split("=", 1)[1])
            index += 1
            continue
        if arg == "--no-color":
            options["colour"] = False
            index += 1
            continue
        if arg == "--verbose":
            options["verbose"] = True
            index += 1
            continue
        if arg == "--ascii":
            options["ascii"] = True
            index += 1
            continue
        if arg == "--version":
            options["version"] = True
            index += 1
            continue
        rest.append(arg)
        index += 1
    return options, rest


def _command(rest: list[str]) -> tuple[str, list[str]]:
    head = rest[0]
    if head in _COMMANDS:
        return head, rest[1:]
    if _INTEGER.fullmatch(head):
        return "inspect", rest
    if head.startswith("-"):
        raise UsageError(f"unrecognised option {head!r}\n{_USAGE.strip()}")
    raise UsageError(f"unrecognised command {head!r}\n{_USAGE.strip()}")


def _find_options(args: list[str]) -> tuple[int, int, int | None, bool]:
    start, end, limit, count_only = 0, 999, None, False
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--start":
            start = _integer(_next(args, index, "start requires an integer"))
            index += 2
        elif arg == "--end":
            end = _integer(_next(args, index, "end requires an integer"))
            index += 2
        elif arg == "--limit":
            limit = _integer(_next(args, index, "limit requires an integer"))
            if limit < 1:
                raise UsageError("limit must be at least 1")
            index += 2
        elif arg == "--count-only":
            count_only = True
            index += 1
        else:
            raise UsageError(f"unrecognised option {arg!r}")
    return start, end, limit, count_only


def _random_options(args: list[str]) -> tuple[int, int, Property | None, int | None]:
    start, end, prop, seed = 0, 999, None, None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--property":
            prop = _named(_next(args, index, "property requires a name"))
            index += 2
        elif arg == "--start":
            start = _integer(_next(args, index, "start requires an integer"))
            index += 2
        elif arg == "--end":
            end = _integer(_next(args, index, "end requires an integer"))
            index += 2
        elif arg == "--seed":
            seed = _integer(_next(args, index, "seed requires an integer"))
            index += 2
        else:
            raise UsageError(f"unrecognised option {arg!r}")
    return start, end, prop, seed


def _check_range(start: int, end: int) -> None:
    if start > end:
        raise UsageError("the start must not exceed the end")
    width = end - start + 1
    if width > MAX_RANGE:
        raise UsageError(
            f"the range contains {width} integers; the maximum is {MAX_RANGE}",
            code=3,
        )


def _format(value: str) -> str:
    if value not in {"text", "json"}:
        raise UsageError("format must be text or json")
    return value


def _integer(arg: str) -> int:
    if not _INTEGER.fullmatch(arg):
        raise UsageError(f"an integer is required, not {arg!r}")
    return int(arg)


def _one(payload: list[str], message: str) -> str:
    _reject_unknown(payload[1:])
    if not payload:
        raise UsageError(message)
    if len(payload) > 1:
        raise UsageError(message)
    return payload[0]


def _reject_unknown(args: list[str]) -> None:
    for arg in args:
        if arg.startswith("-"):
            raise UsageError(f"unrecognised option {arg!r}")


def _next(args: list[str], index: int, message: str) -> str:
    if index + 1 >= len(args):
        raise UsageError(message)
    return args[index + 1]


def _verbose(options: dict[str, object], message: str) -> None:
    if options["verbose"]:
        print(f"number-oddities: {message}", file=sys.stderr)


def _named(name: str) -> Property:
    try:
        return resolve(name)
    except KeyError as exc:
        raise UsageError(f"unknown property {name!r}. Valid properties: {exc.args[0]}") from None
