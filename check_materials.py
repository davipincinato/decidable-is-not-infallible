# SPDX-License-Identifier: MIT
"""Regression check for the teaching materials.

Every claim the notebook makes about what the verifiers do is asserted here. If a
fixture is reworded or a guard is changed, this fails before a learner discovers the
discrepancy mid-exercise.

    python3 check_materials.py

Exits non-zero on the first broken claim.
"""

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

print("\nSection 9 -- and the gap that stays open")
claim("BOTH verifiers pass INC-003 attempt 1 (the definite description)",
      v1("INC-003", 1).passed and v2("INC-003", 1).passed)
claim("that attempt contains no identifier as a literal string",
      all(i not in RECORDED["INC-003"][1]
          for i in REPORTS_BY_ID["INC-003"].identifiers))

print("\nSection 10 -- the boundary moves once the missing fact is supplied")
claim("a knowledge-based check identifies Tomas Lindqvist once crew nationality "
      "is supplied as input",
      flags_by_unique_nationality(RECORDED["INC-003"][1], INC_003_CREW_NATIONALITY)
      == "Tomas Lindqvist")

print("\nSection 12 -- reward under v2 cannot distinguish the leak from the clean pass")
claim("INC-003 attempt 1 (leaks) and attempt 2 (clean) earn identical reward under v2",
      v2("INC-003", 1).passed and v2("INC-003", 2).passed)

print("\nSection 14 -- the same predicate shape gates a JSON payload, not just text")
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

print("\nEvery recorded attempt is reachable and every report terminates cleanly")
for rep in REPORTS:
    attempts = RECORDED[rep.report_id]
    final = verify_v2(attempts[-1], rep.identifiers, rep.essential_facts)
    claim("{}: final recorded attempt passes v2".format(rep.report_id), final.passed)

print()
if FAILURES:
    print("{} broken claim(s):".format(len(FAILURES)))
    for f in FAILURES:
        print("  - " + f)
    sys.exit(1)
print("All claims hold.")
