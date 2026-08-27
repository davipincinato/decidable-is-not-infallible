# SPDX-License-Identifier: MIT
"""Regression check for the teaching materials.

Every claim the notebook makes about what the verifiers do is asserted here. If a
fixture is reworded or a guard is changed, this fails before a learner discovers the
discrepancy mid-exercise.

    python3 check_materials.py

Exits non-zero on the first broken claim.
"""

import re
import sys
from os.path import dirname, join

sys.path.insert(0, dirname(__file__))
sys.path.insert(0, join(dirname(__file__), "solutions"))

from redaction_task import REPORTS, REPORTS_BY_ID          # noqa: E402
from recorded_generator import RECORDED                    # noqa: E402
from solutions.exercises_1_to_3 import (                   # noqa: E402
    verify, verify_v2, repair_loop)
from verifier_reference import (                           # noqa: E402
    verify_extended, INC_003_CREW_NATIONALITY, flags_by_unique_nationality,
    verify_ticket_schema)

FAILURES = []


def claim(description, condition):
    status = "ok  " if condition else "FAIL"
    print("  [{}] {}".format(status, description))
    if not condition:
        FAILURES.append(description)


def v1(rid, i):
    r = REPORTS_BY_ID[rid]
    return verify(RECORDED[rid][i], r.identifiers, r.essential_facts)


def v2(rid, i):
    r = REPORTS_BY_ID[rid]
    return verify_v2(RECORDED[rid][i], r.identifiers, r.essential_facts)


print("\nSection 4 -- the first verifier catches the obvious failures")
claim("INC-001 attempt 0 fails on a surviving identifier",
      not v1("INC-001", 0).passed
      and v1("INC-001", 0).rule == "identifier_survived")
claim("INC-002 attempt 0 fails on a lost fact, not a leak",
      not v1("INC-002", 0).passed and v1("INC-002", 0).rule == "fact_lost")
claim("the failure detail names the specific rule violation",
      "96 files" in v1("INC-002", 0).detail)

print("\nSection 5 -- the repair loop converges as the notebook says")
_, r1, n1 = repair_loop(REPORTS_BY_ID["INC-001"])
_, r2, n2 = repair_loop(REPORTS_BY_ID["INC-002"])
claim("INC-001 converges in exactly 3 attempts", r1.passed and n1 == 3)
claim("INC-002 converges in exactly 2 attempts", r2.passed and n2 == 2)

print("\nSection 6 -- the false negative that motivates the whole notebook")
claim("v1 WRONGLY passes INC-003 attempt 0 (the 'T.L.' initials)",
      v1("INC-003", 0).passed)
claim("all three INC-003 attempts pass v1, so nothing looks wrong",
      all(v1("INC-003", i).passed for i in range(3)))

print("\nSection 7 -- the false alarm, the mirror image")
claim("v1 WRONGLY reports fact_lost on INC-004 attempt 1 ('18,400')",
      not v1("INC-004", 1).passed and v1("INC-004", 1).rule == "fact_lost")
claim("v2 accepts it once separators are normalised", v2("INC-004", 1).passed)

print("\nSection 7 -- the extension does close the gap it targets")
claim("v2 now catches the initials in INC-003 attempt 0",
      not v2("INC-003", 0).passed)

print("\nSection 8 -- the fix has a blind spot too")
claim("the boundary bug (matching a prefix of a longer word) is fixed: "
      "'ITEM' and 'ASAP' do not false-alarm",
      verify_extended("Add this to the ITEM backlog.", ["Ines Torres"], []).passed
      and verify_extended("We need this ASAP please.", ["Ana Silva"], []).passed)
claim("the residual false alarm is real, not hypothetical: bare 'IT' still "
      "collides with the joined-initials form",
      not verify_extended("Escalated to IT support. 12 items.",
                          ["Ines Torres"], ["12 items"]).passed)
claim("the asymmetric-normalisation leak is closed: a comma-separated identifier "
      "no longer survives",
      not verify_extended("The badge is 18,402 and count 18400.",
                          ["18402"], ["18400"]).passed)

print("\nSection 9 -- auditing systematically: the misses")
IDS_TL = ["Tomas Lindqvist", "Lindqvist", "21007"]
claim("case variation is fixed: an uppercase surname no longer survives",
      not verify_extended("LINDQVIST was here", IDS_TL, []).passed)
claim("case variation is fixed: lowercase initials no longer survive",
      not verify_extended("seen with t.l. yesterday", IDS_TL, []).passed)
claim("whitespace variation is fixed: a newline inside the name no longer survives",
      not verify_extended("Tomas\nLindqvist was here", IDS_TL, []).passed)
claim("whitespace variation is fixed: doubled spacing no longer survives",
      not verify_extended("Tomas  Lindqvist was here", IDS_TL, []).passed)
claim("a zero-width space spliced into the surname no longer survives",
      not verify_extended("Lindq​vist was here", IDS_TL, []).passed)
claim("Unicode homoglyphs are the one left open, disclosed rather than patched: "
      "a Cyrillic look-alike for 'T' still survives",
      verify_extended("seen with Т.L. yesterday", IDS_TL, []).passed)

print("\nSection 9 -- auditing systematically: the false alarms, the half that "
      "went unaudited until a reviewer found it")
IDS_COSTA = ["Mariana Costa", "Costa", "88431"]
IDS_RAMAN = ["Priya Raman", "Raman", "OPS-5510"]
claim("a clean rewrite with no identifier in it passes",
      verify_extended("The engineer filed the report that evening.",
                      IDS_TL, []).passed)
claim("the substring false alarm is fixed: 'Costa' no longer fires inside the "
      "unrelated word 'costar'",
      verify_extended("The costar of the drill rig was unavailable.",
                      IDS_COSTA, []).passed)
claim("the whole-word false alarm is real and disclosed (KNOWN_GAPS #5): a bare "
      "surname still collides with an unrelated technical term",
      not verify_extended("Raman spectroscopy equipment failed at 22:40.",
                          IDS_RAMAN, []).passed)
claim("the substring fix did not weaken detection: a genuine surname leak is "
      "still caught",
      not verify_extended("Costa signed off on the rollback.", IDS_COSTA, []).passed)

# The same defect, on the other rule, found one round later --- see KNOWN_GAPS #6.
# The identifier version of this bug false-alarms; the fact version LEAKS, and it
# leaks on accuracy rather than on privacy.
FACTS_INC_001 = ["47 minutes", "1204"]
claim("the fact check has the same boundary guard: a fact corrupted into a longer "
      "number is reported lost, not certified as preserved",
      not verify_extended("the outage ran 147 minutes total",
                          [], FACTS_INC_001[:1]).passed
      and not verify_extended("affecting 51204 transactions",
                              [], FACTS_INC_001[1:]).passed)
claim("that guard did not break the facts as written: the shipped INC-001 facts "
      "still verify against the original report",
      verify_extended(REPORTS_BY_ID["INC-001"].text,
                      [], REPORTS_BY_ID["INC-001"].essential_facts).passed)
claim("the residual is real and disclosed (KNOWN_GAPS #6): a delimiter is a "
      "non-word character, so an extended timestamp still counts as preserved",
      verify_extended("the alert fired at 09:12:45 UTC", [], ["09:12"]).passed)

print("\nSection 10 -- and the gap that stays open")
claim("BOTH verifiers pass INC-003 attempt 1 (the definite description)",
      v1("INC-003", 1).passed and v2("INC-003", 1).passed)
claim("that attempt contains no identifier as a literal string",
      all(i not in RECORDED["INC-003"][1]
          for i in REPORTS_BY_ID["INC-003"].identifiers))

print("\nSection 11 -- the boundary moves once the missing fact is supplied")
claim("a knowledge-based check identifies Tomas Lindqvist once crew nationality "
      "is supplied as input",
      flags_by_unique_nationality(RECORDED["INC-003"][1], INC_003_CREW_NATIONALITY)
      == "Tomas Lindqvist")

print("\nSection 13 -- reward under v2 cannot distinguish the leak from the clean pass")
claim("INC-003 attempt 1 (leaks) and attempt 2 (clean) earn identical reward under v2",
      v2("INC-003", 1).passed and v2("INC-003", 2).passed)

print("\nSection 15 -- the same predicate shape gates a JSON payload, not just text")
claim("a valid ticket passes",
      verify_ticket_schema(
          {"id": "T-1", "severity": "high", "duration_minutes": 47}).passed)
claim("a missing required field fails with the specific rule named",
      not verify_ticket_schema(
          {"severity": "high", "duration_minutes": 47}).passed)
claim("an enum violation and a type violation are told apart, not merged into one rule",
      verify_ticket_schema(
          {"id": "T-3", "severity": "urgent", "duration_minutes": 10}).rule
      != verify_ticket_schema(
          {"id": "T-4", "severity": "low", "duration_minutes": -5}).rule)
claim("the second domain has its own false negative: a low-severity incident running "
      "three days passes every field rule",
      verify_ticket_schema(
          {"id": "T-9", "severity": "low", "duration_minutes": 4320}).passed)
claim("and its mirror image: a high-severity incident resolved in a minute passes too",
      verify_ticket_schema(
          {"id": "T-10", "severity": "high", "duration_minutes": 1}).passed)

print("\nEvery recorded attempt is reachable and every report terminates cleanly")
for rep in REPORTS:
    attempts = RECORDED[rep.report_id]
    final = verify_v2(attempts[-1], rep.identifiers, rep.essential_facts)
    claim("{}: final recorded attempt passes v2".format(rep.report_id), final.passed)


# --------------------------------------------------------------------------------
# The collision sweep --- the checks above are hand-written, and twice now a
# reviewer has found a real gap immediately after one of these lists was declared
# complete. Every claim above is something someone thought to test; this section is
# the part that does not depend on anyone having thought of it. It enumerates,
# rather than spot-checks, and it fails on any collision not already disclosed.
# --------------------------------------------------------------------------------

# Deliberately embedded rather than read from a system dictionary: the package has
# to run offline, on any machine, with nothing installed. Ordinary English words
# that double as surnames, plus scientific terms that are eponyms (the exact class
# a redaction corpus draws names from) and abbreviations common in incident
# reports --- where a two-letter joined-initials form is most likely to collide.
COLLISION_LEXICON = """
baker banks bell bishop black brook brown bush butler chase cook cooper cross day
drake field fisher flint ford frost glass grant gray green hall hand hart hill
hope hunt hunter jordan justice king knight lake lane long mark mars mason may
moore noble page park pike pope port price rand ray reed rice ridge river rose
sage salt sand sharp shore short snow spark stark stone storm street summer swift
tanner tower trace vale wade wall ward waters weaver west wild winter wolf wood
young
ampere angstrom becquerel bohr boyle celsius costa coulomb curie dalton darcy
debye doppler euler farad faraday fermi fourier gauss gibbs hertz hooke joule
kelvin lorentz mach maxwell newton nyquist ohm pascal planck poisson raman
rankine rayleigh reynolds richter siemens sievert stokes tesla volt watt weber
api asap cd ci cpu db eod eta fyi gpu hr http io ip it json kpi mvp os poc pr qa
ram roi sla sql ssd tbd tcp udp ui url ux wip xml yaml
"""

# Every collision the sweep can find must be named in KNOWN_GAPS. Adding a fixture
# identifier that collides with an ordinary word fails this check until the gap is
# either designed out (rename the identifier) or written down (extend KNOWN_GAPS).
DISCLOSED_COLLISIONS = {
    ("Costa", "costa"),        # KNOWN_GAPS #5 -- surname that is also a term
    ("Raman", "raman"),        # KNOWN_GAPS #5 -- the worked example
    ("Priya Raman", "pr"),     # KNOWN_GAPS #3 -- joined initials vs. abbreviation
}


def _collides(identifier, token):
    """Does a sentence whose only candidate match is `token` get rejected?"""
    probe = "Routine note: {} was mentioned in passing.".format(token)
    return not verify_extended(probe, [identifier], []).passed


tokens = sorted({t for t in COLLISION_LEXICON.split() if len(t) >= 2})
found = {(ident, tok)
         for rep in REPORTS
         for ident in rep.identifiers
         for tok in tokens
         if _collides(ident, tok)}

print("\nCollision sweep -- {} fixture identifiers x {} lexicon tokens"
      .format(sum(len(r.identifiers) for r in REPORTS), len(tokens)))
for ident, tok in sorted(found):
    print("       collision: identifier {!r} fires on {!r}".format(ident, tok))
claim("every collision the sweep finds is disclosed in KNOWN_GAPS",
      found <= DISCLOSED_COLLISIONS)
claim("every disclosed collision is still real, so the list has no stale entries",
      DISCLOSED_COLLISIONS <= found)


# --------------------------------------------------------------------------------
# The fact sweep --- the second arm, and the reason it exists is worth stating.
# The sweep above was written to generalise a boundary bug found in the identifier
# check. It enumerates identifiers against words, and only identifiers. The very
# same bug was sitting in the fact check the whole time, and a reviewer found it
# one round later, from the fixtures' own facts. A remedy for a blind spot, built
# with a blind spot. So: facts get enumerated too, against the corruptions that
# a longer number can hide inside.
# --------------------------------------------------------------------------------

_DIGIT_RUN = re.compile(r"\d+")


def _corrupt(fact, kind):
    """Rewrite `fact` into a DIFFERENT value that contains it as a substring.

    Every variant here is wrong: a redaction producing one has changed the number.
    The question each asks is whether the verifier notices.
    """
    if kind == "digit_prefix":       # 47 minutes -> 147 minutes
        return _DIGIT_RUN.sub(lambda m: "1" + m.group(), fact, count=1)
    if kind == "digit_suffix":       # 1204 -> 12045
        runs = list(_DIGIT_RUN.finditer(fact))
        last = runs[-1]
        return fact[:last.end()] + "5" + fact[last.end():]
    if kind == "decimal_extension":  # 1204 -> 1204.5
        runs = list(_DIGIT_RUN.finditer(fact))
        last = runs[-1]
        return fact[:last.end()] + ".5" + fact[last.end():]
    if kind == "delimiter_extension":  # 09:12 -> 09:12:45
        runs = list(_DIGIT_RUN.finditer(fact))
        last = runs[-1]
        return fact[:last.end()] + ":45" + fact[last.end():]
    raise ValueError(kind)


# Which corruption kinds the verifier is expected to MISS, and on which facts. The
# sweep is sharper than the reviewer's two examples and than the first disclosure
# written from them: the leak needs BOTH a corruption that only appends across a
# delimiter AND a fact that ENDS in a digit. "47 minutes" is immune to all four,
# not by any guard, but because corrupting the number leaves the trailing unit word
# no longer adjacent --- the fact stops being a substring at all. Which facts are
# exposed is therefore a property of how the fixture author happened to write them,
# not of the verifier. That is worth failing on if it ever changes.
DISCLOSED_FACT_LEAKS = {"decimal_extension", "delimiter_extension"}  # KNOWN_GAPS #6

FACT_CORRUPTIONS = ["digit_prefix", "digit_suffix",
                    "decimal_extension", "delimiter_extension"]
leaked, mismatches = set(), []
n_facts = 0
for rep in REPORTS:
    for fact in rep.essential_facts:
        if not _DIGIT_RUN.search(fact):
            continue
        n_facts += 1
        ends_in_digit = fact[-1].isdigit()
        for kind in FACT_CORRUPTIONS:
            probe = "Post-incident summary: {} in total.".format(_corrupt(fact, kind))
            leaks = verify_extended(probe, [], [fact]).passed
            expected = kind in DISCLOSED_FACT_LEAKS and ends_in_digit
            if leaks:
                leaked.add(kind)
            if leaks != expected:
                mismatches.append((rep.report_id, fact, kind, leaks))

print("\nFact sweep -- {} numeric fixture facts x {} corruption kinds"
      .format(n_facts, len(FACT_CORRUPTIONS)))
for kind in sorted(leaked):
    print("       leaks: a fact ending in a digit, corrupted by {!r}, still counts "
          "as preserved".format(kind))
for rid, fact, kind, leaks in mismatches:
    print("       UNDISCLOSED: {} {!r} under {!r} -> passed={}"
          .format(rid, fact, kind, leaks))
claim("every corruption the fact sweep finds leaking is disclosed in KNOWN_GAPS",
      leaked <= DISCLOSED_FACT_LEAKS)
claim("every disclosed fact leak is still real, so that list has no stale entries",
      DISCLOSED_FACT_LEAKS <= leaked)
claim("the sweep predicts each of the {} outcomes exactly: a fact leaks if and only "
      "if it ends in a digit and the corruption only appends across a delimiter"
      .format(n_facts * len(FACT_CORRUPTIONS)), not mismatches)

print()
if FAILURES:
    print("{} broken claim(s):".format(len(FAILURES)))
    for f in FAILURES:
        print("  - " + f)
    sys.exit(1)
print("All claims hold.")
