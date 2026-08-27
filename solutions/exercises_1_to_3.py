# SPDX-License-Identifier: MIT
"""Worked solutions to exercises 1-3.

Exercise 4 is open-ended by design and has no solution file; what it asks for is the
learner's own three adversarial cases, written before testing.

These are the same implementations as `verifier_reference.py`, restated here in the
order the notebook builds them so the progression stays readable.
"""

import re
import sys
from os.path import dirname
from typing import List, NamedTuple, Optional

# This file lives one folder below recorded_generator.py (in solutions/), so its
# parent folder needs to be added to the import path before the import below works.
sys.path.insert(0, dirname(dirname(__file__)))

from recorded_generator import RecordedGenerator  # noqa: E402


class Result(NamedTuple):
    passed: bool
    rule: Optional[str] = None
    detail: str = ""


# --------------------------------------------------------------------------------
# Exercise 1 -- the verifier, returning a reason rather than a boolean
# --------------------------------------------------------------------------------

def verify(text: str, identifiers: List[str],
           essential_facts: List[str]) -> Result:
    for ident in identifiers:
        if ident in text:
            return Result(False, "identifier_survived",
                          'The identifier "{}" is still present.'.format(ident))

    for fact in essential_facts:
        if fact not in text:
            return Result(False, "fact_lost",
                          'The essential fact "{}" is missing from your rewrite.'
                          .format(fact))

    return Result(True)


# --------------------------------------------------------------------------------
# Exercise 2 -- the repair loop
# --------------------------------------------------------------------------------

def repair_loop(report, max_iters=3, generator=None):
    """Return (final_text, result, n_attempts).

    The cap is the load-bearing parameter. Without it this is an unbounded spend on a
    model that may never satisfy a constraint it cannot satisfy.

    `generator` defaults to the recorded one. Anything callable as
    `generator(feedback) -> str` works here, which is how `live_generator.py` drops
    in unchanged --- a seam worth noticing.
    """
    if generator is None:
        generator = RecordedGenerator(report.report_id)
    feedback = ""
    text, result = "", Result(False)

    for attempt in range(1, max_iters + 1):
        text = generator(feedback)
        result = verify(text, report.identifiers, report.essential_facts)
        if result.passed:
            return text, result, attempt
        feedback = (
            "Your redaction broke one rule: {}. {} Fix exactly this and change "
            "nothing else.".format(result.rule, result.detail))

    return text, result, max_iters


# --------------------------------------------------------------------------------
# Exercise 3 -- the extended verifier
# --------------------------------------------------------------------------------

def _normalise_numbers(text: str) -> str:
    """18,400 -> 18400, so formatting is not mistaken for deletion."""
    return re.sub(r"(?<=\d)[,\s](?=\d{3}\b)", "", text)


_INVISIBLE_CHARS = "\u200b\u200c\u200d\ufeff"  # ZWSP, ZWNJ, ZWJ, BOM/ZW-no-break-space


def _strip_invisible(text: str) -> str:
    """A zero-width space spliced into a name reads as the name to a human and as a
    different string to `in` --- strip it, and its cousins, before comparing."""
    return text.translate(str.maketrans("", "", _INVISIBLE_CHARS))


def _normalise_whitespace(text: str) -> str:
    """Collapse any run of whitespace to one space."""
    return re.sub(r"\s+", " ", text)


def _contains_as_whole_token(needle: str, haystack: str) -> bool:
    """Bounded by non-word characters, so "Costa" does not fire inside "costar"."""
    return re.search(r"(?<!\w){}(?!\w)".format(re.escape(needle)),
                     haystack) is not None


def _initials_of(name: str) -> List[str]:
    parts = [p for p in name.split() if p]
    if len(parts) < 2:
        return []
    letters = [p[0].upper() for p in parts]
    return [".".join(letters) + ".", ". ".join(letters) + ".", "".join(letters)]


def verify_v2(text: str, identifiers: List[str],
              essential_facts: List[str]) -> Result:
    text = _strip_invisible(text)
    normalised = _normalise_numbers(text)
    identifier_haystack = _normalise_whitespace(normalised).casefold()
    initials_haystack = _normalise_whitespace(text)

    for ident in identifiers:
        if _contains_as_whole_token(ident.casefold(), identifier_haystack):
            return Result(False, "identifier_survived",
                          'The identifier "{}" is still present.'.format(ident))
        for form in _initials_of(ident):
            if re.search(r"\b{}(?!\w)".format(re.escape(form)), initials_haystack,
                        re.IGNORECASE):
                return Result(False, "identifier_survived",
                              'The initials "{}" still identify "{}".'
                              .format(form, ident))

    for fact in essential_facts:
        if fact not in normalised:
            return Result(False, "fact_lost",
                          'The essential fact "{}" is missing from your rewrite.'
                          .format(fact))

    return Result(True)
