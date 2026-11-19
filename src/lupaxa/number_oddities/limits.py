"""Documented safety limits for NumberOddities 1.0.

Complete analysis is guaranteed for every positive integer up to
``COMPLETE_LIMIT``. A single inspection above that limit still tries to
factor the number, but trial division stops at ``FACTOR_TRIAL_LIMIT``.
If that budget cannot prove the factorisation, the result is skipped.
It is never reported as a negative result.

Range searches evaluate at most ``MAX_RANGE`` integers. A search does not
trial-divide candidates above ``COMPLETE_LIMIT``. Those candidates are
skipped for any property that needs a complete factorisation.
"""

from __future__ import annotations

COMPLETE_LIMIT = 1_000_000
FACTOR_TRIAL_LIMIT = 1_000_000
MAX_RANGE = 100_000
# Cube-root loops. 400³ is 64_000_000. 10_000³ is 1_000_000_000_000.
TAXICAB_SEARCH_ROOT = 400
TAXICAB_INSPECT_ROOT = 10_000
# Even digit counts. A 6-digit search tries at most a few hundred fangs.
VAMPIRE_SEARCH_DIGITS = 6
VAMPIRE_INSPECT_DIGITS = 10
