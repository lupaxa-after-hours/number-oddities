<p align="center">
  <a href="https://github.com/lupaxa-after-hours">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/after-hours/readme-logo.png" alt="After Hours" />
  </a>
</p>

<h1 align="center">Number Oddities</h1>

Inspect an integer and see which recreational properties it has. Primes,
perfect numbers, Armstrong numbers, happy numbers, factorions, amicable
pairs, and the rest of a thirty-eight property catalogue. Each match is
explained with the arithmetic, not just a label.

It runs entirely offline. No API keys, no network, and no runtime
dependencies beyond Python 3.11+ and the standard library. It does not
read or write your files.

The PyPI name is `lupaxa-number-oddities`. The import path is
`lupaxa.number_oddities`. The console script is `number-oddities`.
`lupaxa` is a namespace package — there is no `lupaxa/__init__.py`.

## What it Does

Thirty-eight independent checks share one registry. Inspection, search,
comparison, and random discovery all use those same checks.

A property that does not match is left out. A check that cannot be
finished inside the safety limit is marked skipped. It is never reported
as a negative result, and a number is never called composite just because
a primality test stopped early.

Complete analysis is guaranteed for positive integers up to 1,000,000.
Larger integers are handled best-effort. Trial division stops at
1,000,000. A range search accepts at most 100,000 integers. In a range,
vampire checks stop above 6 digits and taxicab checks stop once the cube
root exceeds 400. A single inspection allows 10 vampire digits and a
taxicab cube root of 10,000. Past those limits the property is skipped.

## Install

```bash
pip install lupaxa-number-oddities
```

## Commands

```bash
number-oddities 135
number-oddities inspect 153
number-oddities properties
number-oddities explain disarium
number-oddities find prime --start 0 --end 30
number-oddities compare 28 36
number-oddities random --property happy
```

| Command      | What it Does                                   |
| ------------ | ---------------------------------------------- |
| `<number>`   | Inspect an integer. Same result as `inspect`.  |
| `inspect`    | Inspect an integer and explain every match.    |
| `properties` | List the thirty-eight property identifiers.    |
| `explain`    | Define one property and show a worked example. |
| `find`       | Search an inclusive range, in ascending order. |
| `compare`    | Compare two or more integers.                  |
| `random`     | Pick a number in range that has a property.    |

`find` defaults to 0 through 999. `--limit` stops after that many
matches. `--count-only` scans the whole range and prints the count.

`random` defaults to the same range. `--property` restricts the search.
`--seed` makes the choice repeatable. If nothing in the range qualifies,
the command says so and still exits 0.

| Flag         | Meaning                                                 |
| ------------ | ------------------------------------------------------- |
| `--format`   | `text` or `json`. Accepted before or after the command. |
| `--no-color` | Disable ANSI colours. `NO_COLOR` does the same.         |
| `--ascii`    | Print powers and products with `^` and `*`.             |
| `--verbose`  | Diagnostics on stderr. Tracebacks only with this flag.  |
| `--version`  | Print `number-oddities x.y.z` and exit 0.               |
| `--help`     | Show usage and exit 0.                                  |

## Properties

| Identifier       | Also Called    | Meaning                                                   |
| ---------------- | -------------- | --------------------------------------------------------- |
| `prime`          |                | Greater than 1, with no divisors except 1 and itself.     |
| `composite`      |                | Greater than 1 and not prime. 1 is neither.               |
| `perfect`        |                | Equal to the sum of its proper divisors.                  |
| `abundant`       |                | Proper divisors sum to more than the number.              |
| `deficient`      |                | Proper divisors sum to less than the number.              |
| `perfect_square` | `square`       | Square of an integer. Negatives are not squares.          |
| `perfect_cube`   | `cube`         | Cube of an integer, including negative cubes.             |
| `triangular`     |                | `k(k + 1) / 2` for an integer `k >= 0`.                   |
| `pronic`         |                | `k(k + 1)` for an integer `k >= 0`.                       |
| `fibonacci`      |                | A non-negative Fibonacci number. 0 and 1 qualify.         |
| `palindromic`    | `palindrome`   | Decimal digits read the same both ways.                   |
| `automorphic`    |                | The square ends with the number itself.                   |
| `harshad`        |                | Positive and divisible by the sum of its digits.          |
| `armstrong`      | `narcissistic` | Sum of digits raised to the number of digits.             |
| `disarium`       |                | Sum of digits raised to their positions.                  |
| `kaprekar`       |                | The square splits into two parts that add up to it.       |
| `happy`          |                | Repeated digit-square sums reach 1.                       |
| `smith`          |                | Composite, and the digit sums of the factors agree.       |
| `factorion`      |                | Equal to the sum of the factorials of its digits.         |
| `dudeney`        |                | A cube whose digits sum to the cube root.                 |
| `keith`          |                | Appears in the sequence started by its own digits.        |
| `trimorphic`     |                | The cube ends with the number itself.                     |
| `zuckerman`      |                | Divisible by the product of its non-zero digits.          |
| `spy`            |                | Digit sum equals the digit product. Two digits or more.   |
| `hoax`           |                | Composite, and the distinct prime-factor digits agree.    |
| `amicable`       |                | Proper-divisor sum is a different number that returns it. |
| `vampire`        |                | Two fangs use exactly the digits of the number.           |
| `taxicab`        |                | Two different sums of two positive cubes.                 |
| `emirp`          |                | A non-palindromic prime whose reversal is prime.          |
| `munchhausen`    |                | Digits raised to themselves. A zero digit contributes 0.  |
| `lucas`          |                | A Lucas number. 0 is not one.                             |
| `catalan`        |                | A Catalan number.                                         |
| `pell`           |                | A Pell number. 0 and 1 qualify.                           |
| `factorial`      |                | Some `k!` for `k >= 0`. 0 is not a factorial.             |
| `primorial`      |                | A product of the first `k` primes.                        |
| `sophie_germain` | `germain`      | Prime `p` where `2p + 1` is also prime.                   |
| `semiprime`      |                | Exactly two prime factors, counting repeats.              |
| `sphenic`        |                | Exactly three distinct prime factors.                     |

Zero is a square, a cube, a Fibonacci number, a triangular number, a
pronic number, a Pell number, a Dudeney number, and trimorphic. It is
also palindromic, automorphic, Armstrong, and Disarium. It is not prime,
perfect, Harshad, or happy.

## Examples

### Inspection

```bash
number-oddities 135
```

```text
┌───────────┬───────────────┐
│ Number    │ 135           │
│ Sign      │ positive      │
│ Digits    │ 3             │
│ Digit sum │ 9             │
│ Parity    │ odd           │
│ Factors   │ 3 × 3 × 3 × 5 │
└───────────┴───────────────┘

┌───────────┬────────────────────────────────────────────────────────────────┐
│ Property  │ Explanation                                                    │
├───────────┼────────────────────────────────────────────────────────────────┤
│ Composite │ 135 = 3 × 3 × 3 × 5                                            │
├───────────┼────────────────────────────────────────────────────────────────┤
│ Deficient │ The proper divisors of 135 sum to 105, which is less than 135. │
├───────────┼────────────────────────────────────────────────────────────────┤
│ Harshad   │ 1 + 3 + 5 = 9                                                  │
│           │ 135 ÷ 9 = 15                                                   │
├───────────┼────────────────────────────────────────────────────────────────┤
│ Disarium  │ 1¹ + 3² + 5³                                                   │
│           │ = 1 + 9 + 125                                                  │
│           │ = 135                                                          │
├───────────┼────────────────────────────────────────────────────────────────┤
│ Zuckerman │ 1 × 3 × 5 = 15                                                 │
│           │ 135 ÷ 15 = 9                                                   │
└───────────┴────────────────────────────────────────────────────────────────┘
```

### A Negative Cube

```bash
number-oddities -8
```

```text
┌───────────┬───────────┐
│ Number    │ -8        │
│ Sign      │ negative  │
│ Digits    │ 1         │
│ Digit sum │ 8         │
│ Parity    │ even      │
│ Factors   │ 2 × 2 × 2 │
└───────────┴───────────┘

┌──────────────┬─────────────┐
│ Property     │ Explanation │
├──────────────┼─────────────┤
│ Perfect cube │ -2³ = -8    │
└──────────────┴─────────────┘
```

### Explanation

```bash
number-oddities explain disarium
```

```text
┌─────────────┬─────────────────────────────────────────────────────────────────┐
│ Property    │ Disarium                                                        │
├─────────────┼─────────────────────────────────────────────────────────────────┤
│ Description │ A non-negative integer equal to the sum of its digits raised to │
│             │ their positions.                                                │
├─────────────┼─────────────────────────────────────────────────────────────────┤
│ Example     │ 135                                                             │
├─────────────┼─────────────────────────────────────────────────────────────────┤
│ Explanation │ 1¹ + 3² + 5³                                                    │
│             │ = 1 + 9 + 125                                                   │
│             │ = 135                                                           │
└─────────────┴─────────────────────────────────────────────────────────────────┘
```

### Search

```bash
number-oddities find prime --start 0 --end 30 --limit 5
```

```text
┌──────────┬─────────┐
│ Property │ Prime   │
│ Range    │ 0 to 30 │
│ Matches  │ 5       │
└──────────┴─────────┘

┌───────┐
│ Value │
├───────┤
│     2 │
│     3 │
│     5 │
│     7 │
│    11 │
└───────┘
```

### Comparison

```bash
number-oddities compare 36 28
```

```text
┌────────────────┬─────┬─────┐
│ Property       │  36 │  28 │
├────────────────┼─────┼─────┤
│ Composite      │ yes │ yes │
│ Perfect        │     │ yes │
│ Abundant       │ yes │     │
│ Perfect square │ yes │     │
│ Triangular     │ yes │ yes │
│ Harshad        │ yes │     │
│ Happy          │     │ yes │
│ Keith          │     │ yes │
│ Zuckerman      │ yes │     │
└────────────────┴─────┴─────┘

┌────────┬───────────────────────┐
│ Shared │ Composite, Triangular │
└────────┴───────────────────────┘
```

## Output

`--format text` is the default. `--format json` is the only thing written
to stdout:

```bash
number-oddities inspect 28 --format json
```

The object includes `number`, `basic` (sign, digits, digit sum, parity,
factors, and `factors_status`), `matches` (id, name, explanation), and
`skipped`. A search adds `property`, `start`, `end`, `count`, and
`matches` unless `--count-only` is set.

Text output is a set of aligned tables. `--ascii` draws the rules with
`+`, `-`, and `|`, and replaces `³` and `×` with `^3` and `*`.

## Exit Codes

| Result                                      | Exit |
| ------------------------------------------- | ---- |
| Success, including a search with no matches | 0    |
| Runtime or calculation error                | 1    |
| Invalid arguments or usage                  | 2    |
| Range larger than 100,000 integers          | 3    |

A closed output pipe is still success. A missing number prints usage and
exits 2. An unknown property lists the valid names.

## Library

```python
from lupaxa.number_oddities import evaluate, resolve

status, facts = evaluate(153, resolve("armstrong"))
status  # "match", "miss", or "skipped"
```

`resolve("narcissistic")` returns the Armstrong property. `REGISTRY`
holds all thirty-eight entries. `resolve("germain")` returns the Sophie
Germain property.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
