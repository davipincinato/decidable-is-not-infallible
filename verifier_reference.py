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

This file is illustrative, not production-grade. It exists to teach the pattern and
to give learners something to compare their own implementation against --- not to
redact real incident reports. A deployed redaction gate would need substantially more
coverage than the checks here; `KNOWN_GAPS` documents specific, real ways this one
falls short of that bar, on purpose.
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


_INVISIBLE_CHARS = "\u200b\u200c\u200d\ufeff"  # ZWSP, ZWNJ, ZWJ, BOM/ZW-no-break-space


def _strip_invisible(text: str) -> str:
    """Remove zero-width characters that defeat substring matching without being
    visible to a human reader. A surname with a zero-width space spliced into the
    middle of it reads as itself to a human and as a different string to `in`,
    which is exactly what makes it worth stripping before comparing rather than
    trusting the text as given.
    """
    return text.translate(str.maketrans("", "", _INVISIBLE_CHARS))


def _normalise_whitespace(text: str) -> str:
    """Collapse any run of whitespace --- space, tab, newline --- to one space, so a
    name broken across a line wrap still reads as itself.
    """
    return re.sub(r"\s+", " ", text)


def _contains_as_whole_token(needle: str, haystack: str) -> bool:
    """True when `needle` appears in `haystack` bounded by non-word characters.

    A bare `needle in haystack` fires on an identifier embedded in a longer,
    unrelated word --- "Costa" inside "costar" --- which rejects a redaction that
    removed every real identifier. The lookarounds are the same guard the initials
    check has always had; the identifier check went without one until a reviewer
    found the false alarm. See `KNOWN_GAPS` #5 for what this does *not* fix.
    """
    return re.search(r"(?<!\w){}(?!\w)".format(re.escape(needle)),
                     haystack) is not None


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

    Seven defects have lived here at various points, all caught by review rather
    than by us noticing first, and every one worth naming because this file's own
    coverage list is only as trustworthy as the audit behind it:

    - The initials regex had no trailing boundary, so it matched "IT" as a *prefix*
      of any longer word ("ITEM"), not just the standalone token. Fixed with
      `(?!\\w)`.
    - Number normalisation ran on the fact check only, never on the identifier
      check, so a badge written "18,402" survived detection while "18400" was
      correctly recognised as the preserved fact. Fixed by checking identifiers
      against the same normalised text used for facts.
    - Identifier and initials matching were case-sensitive, so "LINDQVIST" and
      "t.l." both survived undetected. Fixed with `.casefold()` on both sides and
      `re.IGNORECASE` on the initials search.
    - A name broken across a line wrap or written with doubled spacing ("Tomas\\n
      Lindqvist") did not match the single-spaced identifier string. Fixed by
      collapsing whitespace runs before comparing.
    - A zero-width space, non-joiner, joiner, or BOM spliced into a name reads as
      the name to a human and as a different string to `in`. Fixed by stripping
      those code points before comparing.
    - The identifier check was a bare substring test, so any identifier embedded in
      a longer, unrelated word false-alarmed ("Costa" inside "costar"). This is the
      same defect as the initials boundary bug in the first item, in the check that
      matters more, and it went unnoticed for longer because the audit only ever
      tested this check for missed detection. Fixed with the same lookarounds.
    - The FACT check was a bare substring test too, so a fact silently corrupted
      into a longer number still counted as preserved: "47 minutes" was found
      inside "147 minutes", and "1204" inside "51204". Same root cause as the item
      above, opposite direction --- this one LEAKS rather than false-alarms, and it
      leaks on the one property the material calls the whole point of publishing
      the report. It survived the fix above because the fix, and the collision
      sweep written to generalise it, both looked only at identifiers. Fixed with
      the same lookarounds, over the same normalised text; see `KNOWN_GAPS` #6 for
      the part of it that lookarounds do not reach.

    All seven were accidents, not planted traps -- unlike the definite-description
    gap in `KNOWN_GAPS`, which is designed in. Fixing them does not close the
    lesson: all six `KNOWN_GAPS` entries survive on purpose, and #3, #4, #5 and #6
    are the ones that live in the code fixed above rather than beside it.
    """
    text = _strip_invisible(text)
    normalised = _normalise_numbers(text)
    identifier_haystack = _normalise_whitespace(normalised).casefold()
    initials_haystack = _normalise_whitespace(text)

    for ident in identifiers:
        if _contains_as_whole_token(ident.casefold(), identifier_haystack):
            return VerificationResult(
                False, "identifier_survived",
                'The identifier "{}" is still present.'.format(ident))

        # Guard added after attempt 0 of INC-003 passed v1 with "T.L.".
        for form in _initials_of(ident):
            if re.search(r"\b{}(?!\w)".format(re.escape(form)), initials_haystack,
                        re.IGNORECASE):
                return VerificationResult(
                    False, "identifier_survived",
                    'The initials "{}" still identify "{}".'.format(form, ident))

    for fact in essential_facts:
        if not _contains_as_whole_token(fact, normalised):
            return VerificationResult(
                False, "fact_lost",
                'The essential fact "{}" is missing from your rewrite.'.format(fact))

    return VerificationResult(True)


# --------------------------------------------------------------------------------
# What v2 still gets wrong --- read this before trusting it
# --------------------------------------------------------------------------------

KNOWN_GAPS = """
A verifier can be wrong in two directions, and this one is wrong in both. Entries 1,
2, 4 and 6 are text that passes and should not; entries 3 and 5 are clean text that
is WRONGLY REJECTED. The second direction is the one this file's own audit kept
forgetting to look in, which is why #5 spells out how it was missed.

The two rules fail differently, and it is worth keeping them apart. In 1, 2 and 4 an
IDENTIFIER LEAKS. In 6 an identifier does not leak at all --- instead an operational
FACT has been silently corrupted, and the verifier certifies it as preserved. Both
say passed=True; only one of them is about privacy. A reader who collapses the two
directions into "false negative" loses the distinction that decides what a passing
gate is worth.

Only #1 is reachable with the fixtures exactly as they ship. #3 and #5 need one line
of ordinary English (the examples are given). #2, #4 and #6 need a variant of a
fixture, not the fixture itself --- #2 in particular: the shipped INC-004 attempt
writes the badge literally, so both verifiers CATCH it; what leaks is the "18400s"
rephrasing.

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
   it added this rule. Exactly the point Section 12 makes in the abstract, reachable
   here concretely: every rule you add to close a false negative can open a false
   alarm, and this is what one looks like when it is real instead of hypothetical.
   "IT" is not the only instance, and the second one was found by machine rather
   than by us: the collision sweep in `check_materials.py` reports that "Priya
   Raman" generates the joined form "PR", which fires on the ordinary abbreviation
   for public relations. Same class, same absence of a fix, one more reason to
   treat this rule as a trade rather than an improvement.

4. UNICODE HOMOGLYPHS.
   verify_extended("seen with Т.L. yesterday", ["Tomas Lindqvist"], []) still
   passes: that "Т" is Cyrillic capital Te (U+0422), not Latin "T" (U+0054) --
   visually identical in most fonts, a different code point to every check in this
   file. Case-folding and whitespace-collapsing close an entire family of ordinary
   formatting variation (see the audit in the notebook's Section 9); this is not in
   that family. Closing it in general means detecting confusable characters across
   every script that has one, which is an open-ended, actively-adversarial problem
   in its own right (the same one behind lookalike-domain phishing), not a
   normalisation step. This gap is disclosed rather than attempted for exactly that
   reason: a partial fix here would cost real complexity while inviting the same
   false confidence Section 12 warns against. The Cyrillic Te above is one worked
   instance, not a survey: this file has not been pressure-tested against other
   confusable scripts (Greek, full-width Latin, and others each have their own
   lookalikes), and no claim here should be read as covering them.

5. AN IDENTIFIER THAT IS ALSO AN ORDINARY WORD.
   verify_extended("Raman spectroscopy equipment failed during the 22:40 batch
   job.", ["Priya Raman", "Raman", "OPS-5510"], []) returns passed=False on a
   redaction that removed every real identifier: the bare surname "Raman" collides
   with the unrelated technical term "Raman spectroscopy". This is #3's failure
   mode --- a rule closing a false negative opens a false alarm --- but in the
   PRIMARY identifier check rather than the supplementary initials guard, which
   makes it load-bearing rather than peripheral.
   Two halves, and only one of them was fixable. The SUBSTRING half was bounded and
   is now closed: "Costa" inside "costar" no longer fires, because the identifier
   check requires non-word characters on both sides, the guard the initials check
   already had. The WHOLE-WORD half is not reachable that way --- "Raman" is a
   genuine standalone token in both the identifier and the collision, exactly as
   "IT" is in #3. Separating "Raman the person" from "Raman the scattering effect"
   is named-entity disambiguation, a research problem, not a regex. A denylist of
   known collisions would close these two examples and generalise to nothing.
   HOW THIS WAS FOUND, AND WHAT THAT SAYS ABOUT THE AUDIT ITSELF: a reviewer hit it
   on a first attempt, using the fixtures' own identifiers, after the Section 9
   audit had been declared complete. The audit was asymmetric. It tested the
   identifier check for MISSED DETECTION (casing, whitespace, invisible characters,
   look-alikes) and the initials guard for OVER-TRIGGERING (#3), and never tested
   the identifier check for over-triggering --- the one cell of that grid nobody
   filled in. That asymmetry, not the collision, is the real defect here: a
   checklist you wrote yourself inherits the blind spots of the person who wrote it.
   `check_materials.py` now sweeps every fixture identifier against a lexicon of
   ordinary words and technical terms and fails unless every collision it finds is
   named in this list --- which is how "PR" in #3 turned up.

6. A FACT SWALLOWED BY A LONGER NUMBER ACROSS A DELIMITER.
   verify_extended("the alert fired at 09:12:45 UTC", [], ["09:12"]) returns
   passed=True, and so does the same call with "1204" against "a rate of 1204.5 per
   second". The fact check now requires non-word characters on both sides, which is
   what stopped "47 minutes" from being found inside "147 minutes". But ":" and "."
   ARE non-word characters, so a timestamp extended into a more precise one, or a
   count extended into a decimal, still satisfies the boundary and still counts as
   preserved. The rewrite has changed the number and the gate certifies that it did
   not.
   WHICH FACTS ARE EXPOSED IS AN ACCIDENT OF HOW THEY WERE WRITTEN. The sweep in
   `check_materials.py` runs all four corruptions over all sixteen numeric fixture
   facts and the result is exactly predictable: a fact leaks if and only if it ENDS
   in a digit. "1204", "09:12" and "14 March 2024" leak; "47 minutes", "3 times" and
   "96 files" survive every corruption -- not because any guard protects them, but
   because corrupting the number leaves the trailing unit word no longer adjacent,
   so the fact stops being a substring at all. Half this list is safe for a reason
   that has nothing to do with the verifier. Read that as the general case: coverage
   you did not design is coverage you cannot rely on, and the same list of facts
   written as bare numbers would leak straight through.
   What separates this from the half that was fixed is not difficulty, it is
   DECIDABILITY WITHOUT MORE INPUT. "147" is not "47" under any reading, so a rule
   can say so. Whether "09:12:45" preserves "09:12" or replaces it depends on what
   the fact was FOR --- the minute the page fired, in which case it is preserved, or
   the timestamp of record, in which case it is not. Nothing in `essential_facts`
   says which, because a bare string cannot: the list gives the verifier text to
   match and no type, no unit, no tolerance. Closing this properly means facts stop
   being strings and start being typed values with a comparison rule each, which is
   a different design for the whole interface, not a lookaround.
   HOW THIS WAS FOUND: a reviewer, from the fixtures' own facts, one round after the
   identifier-side version of exactly this bug had been fixed AND generalised into
   the collision sweep. The sweep enumerates identifiers against a word lexicon; it
   had no fact arm at all. So the remedy written to cure a blind spot was itself
   built with one, and the class of bug it was written to catch survived on the
   other rule for a full round. `check_materials.py` now sweeps facts against
   digit-extension variants as well --- but the honest reading is the one Section 12
   argues: each of these sweeps covers the failure that was just demonstrated to us,
   which is not the same as covering the failure.

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
# world. See KNOWN_GAPS #1 and the notebook's Section 11.
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
# Section 15. Not an exercise: shown once as a fact, not asked of the learner twice.
#
# It carries its own false negative on purpose, and the notebook runs it:
# {"id": "T-9", "severity": "low", "duration_minutes": 4320} passes every rule below
# --- id present, severity in the enum, duration a positive integer --- and describes
# a low-severity incident running three days. Each field is checked against its own
# rule; no rule checks two fields against EACH OTHER. That is `T.L.` in a domain
# sharing no code with redaction, which is the point of showing it: the gap is a
# property of writing predicates, not a property of text matching. The bounded fix is
# a severity/duration consistency rule; past it sits the undecidable half --- whether
# the severity label is right for the incident it describes, which the payload never
# states. Left unfixed deliberately: the learner is asked to see it, not to patch it.
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
