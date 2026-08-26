# SPDX-License-Identifier: MIT
"""Reference verifiers --- the instructor's copy.

Learners write their own in the notebook; this file is what they compare against
afterwards. It holds two verifiers on purpose, because the interesting lesson is
the distance between them, and the fact that the distance does not close.

    verify_naive     -- literal substring matching. What almost everyone writes first.
    verify_extended  -- normalises number formatting, catches initials.

`verify_extended` fixes every failure `verify_naive` has on these four reports, and
still misses one, and the miss is documented rather than patched. That is not a gap
left for tidiness: patching it would replace an honest boundary with the illusion
that one more rule finishes the job.
"""

import re
from typing import List, NamedTuple, Optional


class VerificationResult(NamedTuple):
    """A verdict plus the reason for it.

    The reason is the part that matters. A verifier returning True/False can gate a
    loop but cannot drive one --- the generator needs to know *which* rule broke, in
    words specific enough to act on. Everything the repair prompt says comes from
    here.
    """

    passed: bool
    rule: Optional[str] = None  # "identifier_survived" | "fact_lost"
    detail: str = ""

    def as_feedback(self) -> str:
        """The message handed back to the generator on failure."""
        if self.passed:
            return ""
        return "Your redaction broke one rule: {}. {} Fix exactly this and change " \
               "nothing else.".format(self.rule, self.detail)


# --------------------------------------------------------------------------------
# v1 -- the naive verifier
# --------------------------------------------------------------------------------

def verify_naive(text: str, identifiers: List[str],
                 essential_facts: List[str]) -> VerificationResult:
    """Literal substring matching, both directions."""
    for ident in identifiers:
        if ident in text:
            return VerificationResult(
                False, "identifier_survived",
                'The identifier "{}" is still present.'.format(ident))

    for fact in essential_facts:
        if fact not in text:
            return VerificationResult(
                False, "fact_lost",
                'The essential fact "{}" is missing from your rewrite.'.format(fact))

    return VerificationResult(True)


# --------------------------------------------------------------------------------
# v2 -- the extended verifier
# --------------------------------------------------------------------------------

def _normalise_numbers(text: str) -> str:
    """Strip thousands separators (comma or space) so 18,400 and 18 400
    both compare equal to 18400.

    Motivated by a real false alarm: a redaction that preserved a count perfectly was
    sent back for repair because the model wrote it with a comma.
    """
    return re.sub(r"(?<=\d)[,\s](?=\d{3}\b)", "", text)


def _initials_of(name: str) -> List[str]:
    """Plausible initial-forms of a full name: 'Tomas Lindqvist' -> T.L., T. L., TL."""
    parts = [p for p in name.split() if p]
    if len(parts) < 2:
        return []
    letters = [p[0].upper() for p in parts]
    joined = "".join(letters)
    return [
        ".".join(letters) + ".",  # T.L.
        ". ".join(letters) + ".",  # T. L.
        joined,  # TL
    ]


def verify_extended(text: str, identifiers: List[str],
                    essential_facts: List[str]) -> VerificationResult:
    """Normalises number formatting and catches initial-forms of names.

    Two defects lived here until a review caught them, and both are worth naming
    because they are exactly the lesson this file teaches, aimed at itself:

    - The initials regex had no trailing boundary, so it matched "IT" as a *prefix*
      of any longer word ("ITEM"), not just the standalone token. Fixed with
      `(?!\\w)`.
    - Number normalisation ran on the fact check only, never on the identifier
      check, so a badge written "18,402" survived detection while "18400" was
      correctly recognised as the preserved fact. Fixed by checking identifiers
      against the same normalised text used for facts.

    Both were accidents, not planted traps -- unlike the definite-description gap in
    `KNOWN_GAPS`, which is designed in. Fixing them does not close the lesson; see
    `KNOWN_GAPS` #3 for the false alarm that survives the fix on purpose.
    """
    normalised = _normalise_numbers(text)

    for ident in identifiers:
        if ident in normalised:
            return VerificationResult(
                False, "identifier_survived",
                'The identifier "{}" is still present.'.format(ident))

        # Guard added after attempt 0 of INC-003 passed v1 with "T.L.".
        for form in _initials_of(ident):
            if re.search(r"\b{}(?!\w)".format(re.escape(form)), text):
                return VerificationResult(
                    False, "identifier_survived",
                    'The initials "{}" still identify "{}".'.format(form, ident))

    for fact in essential_facts:
        if fact not in normalised:
            return VerificationResult(
                False, "fact_lost",
                'The essential fact "{}" is missing from your rewrite.'.format(fact))

    return VerificationResult(True)


# --------------------------------------------------------------------------------
# What v2 still misses --- read this before trusting it
# --------------------------------------------------------------------------------

KNOWN_GAPS = """
Both verifiers pass text that leaks. Two are reachable in the fixtures:

1. DEFINITE DESCRIPTIONS (INC-003, attempt 1).
   "the only Swedish engineer on the migration crew" contains no identifier as a
   string, and identifies exactly one person. Unlike the initials guard above, this
   is not a computable transformation of a string already in `identifiers` --- nothing
   connects the two strings. Identifying the person needs a fact about the crew that
   lives nowhere in the input, so no amount of string matching reaches this.

2. RECOVERABLE PARAPHRASE OF A NUMBER (INC-004, attempt 0).
   "in the 18402 range" -- here the literal survives, so v1 does catch it. But the
   same trick with "in the 18400s" would not, and neither would "one above the
   duplicate count". A number can be specified without being written.

3. THE INITIALS GUARD FALSE-ALARMS ON ORDINARY SHORT WORDS.
   Fixing the boundary bug above (`(?!\\w)`) stopped "IT" from matching inside
   "ITEM", but it cannot stop "IT" from matching as its own, genuinely standalone
   word -- verify_extended("Escalated to IT support.", ["Ines Torres"], []) still
   flags "IT" as surviving initials. This is not left over from the bug; it is what
   is left AFTER the bug is fixed. A bare two-letter joined form (no periods) is
   indistinguishable from an ordinary two-letter word by string matching alone --
   there is no regex fix, only a coverage-vs-precision trade the extension made when
   it added this rule. Exactly the point Section 9 makes in the abstract, reachable
   here concretely: every rule you add to close a false negative can open a false
   alarm, and this is what one looks like when it is real instead of hypothetical.

The instinct on reading this is to add more rules. Resist it long enough to ask what
the next gap would be. The reports here were written by us; a real corpus supplies
formats nobody thought to anticipate, indefinitely.

The honest summary a verifier can support is: NO OUTPUT CONTAINS A LEAK OF A FORM I
CHECK FOR. Not: no output leaks. The first is a fact. The second is a hope, and the
gap between them is exactly the set of formats you did not think of.
"""


# --------------------------------------------------------------------------------
# What moves the boundary --- a knowledge-based check over the same definite
# description, once the missing fact is supplied as input instead of left in the
# world. See KNOWN_GAPS #1 and the notebook's Section 10.
# --------------------------------------------------------------------------------

INC_003_CREW_NATIONALITY = {
    "Tomas Lindqvist": "Swedish",
    "Priya Raman": "Indian",
    "Diego Fernandez": "Argentine",
    "Wei Zhang": "Chinese",
}


def flags_by_unique_nationality(text: str, crew_nationality: dict) -> Optional[str]:
    '''Return the crew member a "the only <X> ... crew" phrase would identify, if any.

    Decidable now for exactly the reason it was not decidable before: the fact that
    makes the phrase identifying --- which nationality is unique on the crew --- is
    now part of the input, not just part of the world.
    '''
    from collections import Counter
    counts = Counter(crew_nationality.values())
    for name, nat in crew_nationality.items():
        if counts[nat] == 1 and "only {} engineer".format(nat.lower()) in text.lower():
            return name
    return None


# --------------------------------------------------------------------------------
# The skeleton is not tied to redaction --- the same predicate shape (structured
# reason, not a boolean) gating a JSON payload against a schema. See the notebook's
# Section 14. Not an exercise: shown once as a fact, not asked of the learner twice.
# --------------------------------------------------------------------------------

def verify_ticket_schema(payload: dict) -> VerificationResult:
    if "id" not in payload:
        return VerificationResult(
            False, "missing_field", 'Required field "id" is absent.')
    if payload.get("severity") not in ("low", "medium", "high"):
        return VerificationResult(
            False, "invalid_enum",
            '"severity" must be low/medium/high, got {!r}.'.format(
                payload.get("severity")))
    if (not isinstance(payload.get("duration_minutes"), int)
            or payload["duration_minutes"] <= 0):
        return VerificationResult(
            False, "invalid_type", '"duration_minutes" must be a positive integer.')
    return VerificationResult(True)
