# SPDX-License-Identifier: MIT
"""Builds 01_verifier_as_gate.ipynb.

The notebook is generated rather than hand-edited so that it stays reviewable in
git and so that every code cell can be executed as part of the build check. Run:

    python3 build_notebook.py && python3 check_materials.py
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
c = []


def md(text):
    c.append(nbf.v4.new_markdown_cell(text.strip(), id="c{:02d}".format(len(c))))


def code(text):
    c.append(nbf.v4.new_code_cell(text.strip(), id="c{:02d}".format(len(c))))


# --------------------------------------------------------------------------------
md(r"""
# Decidable is not infallible

### Writing a verifier that gates a language model — and finding out what it misses

You will build a program that decides whether a model's output is acceptable, feed its
verdict back to the model, and watch the output get fixed. Then you will find an output
your program accepts and should not, and you will have to decide what to do about it.

That last part is the point of this notebook. The loop is easy. Knowing what it
guarantees is not.

**Time:** ~80 minutes for Sections 1-12 (Exercises 1-3 and the discussion). Exercise 4
is intentionally open-ended and typically needs 45+ minutes on its own --- plan it as a
second session or take-home rather than folding it into the same sitting. See
`02_FACILITATOR_GUIDE.md` for a per-section breakdown. **Prerequisites:** Python
(functions, strings, lists) and a rough idea of what an LLM API call does. Nothing else.

**Cost:** zero. Every model output here is a recording. No API key, no spending.
""")

md(r"""
## 1. A task with two constraints

An operations team wants to publish its incident write-ups. Before anything goes out,
each report has to lose its direct identifiers — names, badge numbers, ticket IDs — and
keep every operational fact, because the facts are the reason to publish at all.

Two constraints, pulling opposite ways. Let us look at one.
""")

code(r"""
try:
    from redaction_task import REPORTS_BY_ID
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Could not import redaction_task. Launch Jupyter from inside the "
        "materiais/ folder these files live in (see README.md), then re-run "
        "this cell."
    ) from exc

report = REPORTS_BY_ID["INC-001"]

print(report.text)
print()
print("must NOT survive:", report.identifiers)
print("must survive:    ", report.essential_facts)
""")

md(r"""
Notice what we have that is unusual: **the ground truth is attached**. We are not asking
anyone to guess which words were identifying. We already know, because the team knows
who wrote the report.

Hold on to that. It is the entire reason the rest of this notebook works.
""")

md(r"""
## 2. The reflex, and why it is worth resisting

Ask a room of engineers how to check whether the redaction worked and most will reach
for the same thing: send the original and the rewrite to a language model and ask *did
this preserve the facts and remove the names?*

That approach has real uses. This is not one of them, for three reasons:

1. **It costs money per check**, forever, including every retry.
2. **It is not exact.** The judge is a model, so it has an error rate on a question that
   has a definite answer.
3. **It is circular where it hurts most.** If the same family of model both writes the
   redaction and grades it, a blind spot in one is likely a blind spot in the other.

Compare that to what we actually need to decide: *does the string `88431` appear in this
text?* You do not need a language model for that. You need `in`.
""")

md(r"""
## 3. The condition that changes everything

> When the property you care about is **decidable in code** from information you already
> have, a program can decide it — exactly, for free, every time.

"Decidable in code" is doing real work in that sentence, and later in this notebook we
will watch it stop being true. For now: we know the identifiers and we know the facts,
so both halves reduce to string containment.

This is the same structure behind **verifiable rewards** — the idea that if you can
*check* an output programmatically, you can train or steer a model against that check
instead of against a learned preference model. Same insight, different scale.
""")

md(r"""
## 4. Exercise 1 — write the verifier

Write `verify(text, identifiers, essential_facts)`.

One design constraint, and it matters more than it looks: **do not return a boolean.**
Return the verdict *and the reason*. A verifier that says `False` can stop a loop but
cannot drive one — the model needs to know which rule it broke, in words specific enough
to act on.
""")

code(r"""
from typing import List, NamedTuple, Optional


# A NamedTuple is a plain class whose fields you read by name (result.passed,
# result.rule), and whose printed form already shows those names -- inspect what
# you built just by looking at the output.
class Result(NamedTuple):
    passed: bool
    rule: Optional[str] = None      # "identifier_survived" | "fact_lost"
    detail: str = ""


def verify(text: str, identifiers: List[str], essential_facts: List[str]) -> Result:
    # TODO
    # 1. If any identifier still appears in `text`, fail with rule="identifier_survived"
    #    and a detail naming which one.
    # 2. If any essential fact is missing from `text`, fail with rule="fact_lost"
    #    and a detail naming which one.
    # 3. Otherwise pass.
    raise NotImplementedError


# Check yourself: this attempt left the surname in.
from recorded_generator import RECORDED

attempt = RECORDED["INC-001"][0]
print(attempt)
print()
print(verify(attempt, report.identifiers, report.essential_facts))
""")

md(r"""
Expected: a failure naming `Costa`.

Once that works, try `RECORDED["INC-002"][0]`. It removes every identifier cleanly — and
still fails. Read the rewrite and see if you can tell why before you run it.
""")

code(r"""
inc2 = REPORTS_BY_ID["INC-002"]
print(RECORDED["INC-002"][0])
print()
print(verify(RECORDED["INC-002"][0], inc2.identifiers, inc2.essential_facts))
""")

md(r"""
The redaction succeeded and the report became worthless: `96 files` is gone. A verifier
that only checked for leaks would have called this a clean pass.

Most of the value in a verifier is in the constraint you *nearly forgot to write down*.
""")

md(r"""
## 5. Exercise 2 — close the loop

Now use the reason. Feed it back, let the model try again, verify again, stop when it
passes or when you run out of patience.

That last clause is not optional. A repair loop with no iteration cap is a way to spend
money until someone notices.
""")

code(r"""
from recorded_generator import RecordedGenerator


def repair_loop(report, max_iters=3, generator=None):
    '''Return (final_text, result, n_attempts).'''
    if generator is None:
        generator = RecordedGenerator(report.report_id)
    feedback = ""
    # TODO
    # Up to max_iters times:
    #   - text = generator(feedback)
    #   - result = verify(text, report.identifiers, report.essential_facts)
    #   - if result.passed: return it
    #   - otherwise build feedback from result.rule and result.detail
    # If the cap is reached without passing, return the last attempt and its result.
    raise NotImplementedError


for rid in ["INC-001", "INC-002"]:
    text, result, n = repair_loop(REPORTS_BY_ID[rid])
    print("{}: passed={} after {} attempt(s)".format(rid, result.passed, n))
""")

md(r"""
`INC-001` should take three attempts, `INC-002` two.

**One caveat, stated plainly because it would be easy to hide:** these are recordings.
A recorded generator cannot actually read your feedback — it replays what a model did
when it was given feedback of this kind. The *shape* of the loop is faithful; the
responsiveness is simulated. With a live model, phrasing the feedback well changes how
fast this converges, and that is worth trying if you have a key.
""")

md(r"""
## 6. Now the interesting part

Run your verifier over every recorded attempt for `INC-003`. All three pass.

Read them.
""")

code(r"""
inc3 = REPORTS_BY_ID["INC-003"]
for i, att in enumerate(RECORDED["INC-003"]):
    r = verify(att, inc3.identifiers, inc3.essential_facts)
    print("--- attempt {} : passed={}".format(i, r.passed))
    print(att)
    print()
""")

md(r"""
**Before you read the next cell:** pick one attempt above and write down, in one
sentence, who it identifies and how — not "it looks off," a specific claim you could
be wrong about. There is no code to run for this. The point is to commit to a guess
before finding out whether it was right; skimming straight past this line gives away
the exercise.
""")

md(r"""
Attempt 0 refers to **`T.L.`**

Your verifier looked for `Tomas Lindqvist` and for `Lindqvist`, found neither, and
passed the text. On a crew with one Lindqvist, `T.L.` identifies him precisely. The
verifier is not broken — it did exactly what you wrote. It just never claimed what you
assumed it claimed.

This is a **false negative**: an output that passes and should not. (The convention
here: the verifier tests for a leak, so a leak is the positive case, and passing text
that leaks is a miss on that positive — the same sense as a scanner missing a real
vulnerability.) In a gate, these are the dangerous ones. A false *alarm* costs you a
wasted retry. A false negative ships.
""")

md(r"""
## 7. Exercise 3 — extend it

Add an initials guard. `Tomas Lindqvist` should also be caught as `T.L.`, `T. L.`, `TL`.

While you are there, run `INC-004` attempt 1 through your current verifier first.
""")

code(r"""
inc4 = REPORTS_BY_ID["INC-004"]
print(RECORDED["INC-004"][1])
print()
print(verify(RECORDED["INC-004"][1], inc4.identifiers, inc4.essential_facts))
""")

md(r"""
It reports `18400` as lost. It is not lost — the model wrote it `18,400`.

That is the mirror image of the `T.L.` problem: a **false alarm**, sending a perfectly
good redaction back for repair. Cheap in this notebook, expensive at scale, and it
biases the "how many iterations to converge" number you would otherwise report.

So there are two fixes to make: normalise thousands separators before checking facts,
and catch initials before passing identifiers.

Two ways to do the first one. Either is a correct answer to this exercise.

**The direct way:** every number in these four reports is written with either a comma
or nothing at all, so `text.replace(",", "")` strips every thousands separator you
will actually see here. No regex required.

**The general way**, if you want a tool that also handles a separator you have not
seen yet (a space, say): `re.sub(pattern, "", text)` deletes every match of `pattern`.
The pattern `r"(?<=\d)[,\s](?=\d{3}\b)"` reads as *a comma or whitespace character,
but only when it sits right after a digit and right before exactly three digits and a
word boundary*. `(?<=\d)` is a **lookbehind** --- "require a digit here, but do not
consume it as part of the match." `(?=\d{3}\b)` is a **lookahead** --- the same idea,
looking forward. Lookbehind/lookahead let a regex require context around a match
without deleting that context along with it.
""")

code(r"""
import re


def verify_v2(text: str, identifiers: List[str], essential_facts: List[str]) -> Result:
    # TODO
    # Start from your `verify`, then:
    #   - before checking facts, strip thousands separators: 18,400 -> 18400
    #     (`text.replace(",", "")` is enough for this exercise -- see the note
    #     above for the general regex version if you want it)
    #   - for each identifier with 2+ words, also reject "T.L.", "T. L." and "TL"
    raise NotImplementedError


for i, att in enumerate(RECORDED["INC-003"]):
    print("INC-003 attempt {}: v1={} v2={}".format(
        i,
        verify(att, inc3.identifiers, inc3.essential_facts).passed,
        verify_v2(att, inc3.identifiers, inc3.essential_facts).passed))

print()
for i, att in enumerate(RECORDED["INC-004"]):
    print("INC-004 attempt {}: v1={} v2={}".format(
        i,
        verify(att, inc4.identifiers, inc4.essential_facts).passed,
        verify_v2(att, inc4.identifiers, inc4.essential_facts).passed))
""")

md(r"""
Expected for `INC-003`: `True False`, `True True`, `True True` --- same as before
(v1 still wrongly passes attempt 0; v2 now catches it).

Expected for `INC-004`: `False False`, `False True`, `True True`. The middle line is
the one that matters: `v1` should stay `False` (it still reports the `18,400` false
alarm) while `v2` flips to `True` (your normalisation fixed it). **If your `v2` is
still `False` on attempt 1, your number normalisation has a bug** --- the `INC-003`
loop above never exercises that code path, only this one does.
""")

md(r"""
## 8. The fix has a blind spot too

Before moving on: run your `verify_v2` on two sentences that have nothing to do with
these reports.
""")

code(r"""
print(verify_v2("Escalated to IT support. 12 items.", ["Ines Torres"], ["12 items"]))
print(verify_v2("We need this ASAP please.", ["Ana Silva"], []))
""")

md(r"""
The second call passes, as it should — `ASAP` is not `Ana Silva`'s initials, it just
happens to start with the same two letters. The first one does not. Your verifier just
told you `"Ines Torres"` is still identified in a sentence about a help desk, because it
contains the word "IT".

This is not the same bug as the false alarm you just fixed. If your initials guard still
matched `IT` as a *prefix* of a longer word like `ITEM`, that was a boundary bug in the
regex, and it is worth fixing (add a check that the match is not immediately followed by
another letter or digit). But once that is fixed, `IT` **on its own** still matches, and
there is no regex left to fix it with: a bare two-letter joined form — no periods, no
spaces — is a string like any other, and "IT" the department is spelled exactly like
"IT" the initials of "Ines Torres". Nothing in the input tells you which one a reader
would mean.

Section 11 will make a general claim about extensions and coverage. This is what that
claim looks like when it is not hypothetical: the exact rule you added in this exercise
to close a false negative can open a false alarm of its own, in text the rule was never
about. Extending a verifier does not make it strictly better along every axis — the
guard that catches `T.L.` is inseparable from the guard that misreads `IT`.
""")

md(r"""
## 9. The part that does not have a fix

Your `verify_v2` now catches `T.L.` Run it on `INC-003` attempt 1 again.

It passes. Read it:

> *"the only Swedish engineer on the migration crew observed replication lag..."*

No name. No initials. No badge. Zero identifiers as strings — and it identifies one
person exactly, to anyone who knows the team.

**This is a different kind of gap from the one you just closed.** `T.L.` was still
decidable from what you had: it is a fixed, computable transformation of a string
already in `identifiers`, so you could enumerate it and check for it without knowing
anything about the crew. "The only Swedish engineer on the migration crew" is not a
transformation of `"Tomas Lindqvist"` at all — nothing connects the two strings.
Knowing that the phrase identifies him needs a fact (who is on the crew, and where
they are from) that lives nowhere in your input: not in the text, not in
`identifiers`, not in `essential_facts`. No amount of string matching reaches this —
not because you have not tried hard enough, but because the input no longer contains
what deciding the question would require. Section 3 promised the condition would stop
being true; here is where.

The instinct is to add a third rule. Before you do, answer this: what would the *fourth*
gap be? These four reports were written by us, and we planted the traps we knew about. A
real corpus supplies formats nobody thought to anticipate, indefinitely.
""")

md(r"""
## 10. What the boundary looks like once you add information

Section 9 called this gap unreachable by string matching, and it is — from what
`verify_v2` is given. That is not the same as unreachable, period. Watch what happens
when the input grows by exactly one fact.
""")

code(r"""
# Not part of `identifiers` or `essential_facts` --- a fact about the crew, supplied
# separately, the way a real deployment might pull it from an HR system.
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


perifrase = RECORDED["INC-003"][1]
print(flags_by_unique_nationality(perifrase, INC_003_CREW_NATIONALITY))
""")

md(r"""
Expected: `Tomas Lindqvist`. Supplying the roster did not make string matching cleverer
— it moved the fact that was missing from "the world" into "the input", which is the
only kind of move that ever restores decidability. This is the third row of the table
in the two-page description: a knowledge-based check, exact *if the fact is supplied*.

It is also why this is not a satisfying general fix. It closes exactly the phrasing you
anticipated ("the only \<nationality\> engineer") and needs a new roster fact for every
category a description might use — role, seniority, shift, whatever else uniquely
identifies someone on a given team. The boundary moved; it did not disappear.
""")

md(r"""
## 11. What a verifier actually buys you

Here is the claim a verifier supports:

> **No output contains a leak of a form I check for.**

And here is the claim people hear:

> ~~No output leaks.~~

The first is a fact you can stand behind. The second is a hope. The gap between them is
exactly the set of formats you did not think of — which, by construction, you cannot
measure from inside the system.

None of this makes verifiers a bad idea. Against an LLM judge, a deterministic gate is
still exact where it applies, free, reproducible, and honest about its own scope in a
way a judge cannot be. What changes is the sentence you are entitled to write in the
results section.

The engineering decision that follows — **extend the predicate, or document the
limitation** — is a real fork, and the honest answer is not always "extend". Each new
rule adds surface area, can introduce false alarms of its own, and, worst of all, grows
your confidence faster than it grows your coverage. At some point the useful move is to
write down what the gate does not cover and stop pretending otherwise.
""")

md(r"""
## 12. What happens when you optimise against this

Everything so far used the verifier to gate a fixed set of recordings: read the
feedback, hand-pick the next attempt. RLVR does something structurally different — it
scores many attempts with a verifier like this one and adjusts a model to produce more
of what scores well. Nothing here trains anything. But the same recordings let you
compute the one number that decides whether that would go well: the reward each
attempt earns, next to whether it actually leaks.
""")

code(r"""
inc3_attempts = RECORDED["INC-003"]
leaks_on_inspection = [True, True, False]  # read by us; not derived from any verifier

print("{:<10} {:>16} {:>12} {:>12}".format(
    "attempt", "actually leaks", "reward(v1)", "reward(v2)"))
for i, att in enumerate(inc3_attempts):
    reward_v1 = int(verify(att, inc3.identifiers, inc3.essential_facts).passed)
    reward_v2 = int(verify_v2(att, inc3.identifiers, inc3.essential_facts).passed)
    print("{:<10} {:>16} {:>12} {:>12}".format(
        i, str(leaks_on_inspection[i]), reward_v1, reward_v2))
""")

md(r"""
Read the `reward(v2)` column against `actually leaks`. Attempt 1 leaks — a human reading
it identifies Tomas Lindqvist immediately — and it earns exactly the same reward as
attempt 2, which does not leak at all. To anything optimising `reward(v2)`, these two
outputs are indistinguishable: identical score, no gradient between them.

That is the concrete shape of the closing claim in Section 11. It is not that a trained
model *might stumble onto* the gap by bad luck. There is no signal anywhere in this
reward pointing away from attempt 1 — optimising against `v2` is not more likely to
avoid the leak than to reproduce it, because the reward cannot tell them apart. A
verifiable reward is exact on what it checks and *silent*, not cautious, on what it does
not: silence looks identical to safety until you check by hand, which is the one thing
the whole point of automating this was to avoid doing at scale.

DeepSeek-R1 (Guo et al., 2025 — full citation in the two-page description) chose
rule-based verification over a learned reward model for this exact reason: a neural
reward model can be gamed in ways that are hard to detect, while a rule-based one is at
least exact about what it rewards. This cell is what that trade looks like from the
other side: exact-and-narrow beats approximate-and-broad on the cases a rule covers, and
produces a real blind spot, not a smaller one, on the cases it does not.
""")

md(r"""
## 13. Exercise 4 — your own gate

Pick a constraint from your own work where the ground truth is available:

- unit tests that generated code must pass
- a JSON schema an output must validate against
- a summary that must not introduce numbers absent from the source
- a translation that must preserve every named entity

Then write, in this order:

1. The predicate, returning a structured reason.
2. **Three inputs you expect it to wrongly accept.** Write these *before* you test it.
3. The results — did it accept them?
4. One paragraph: extend, or document? Defend the choice.

Step 2 is the exercise. Anyone can write a verifier that passes its own tests.

Instructors: a grading rubric for this exercise is in `03_rubric_exercise_4.md`.
""")

md(r"""
## 14. The skeleton is not tied to redaction

Everything above --- `Result`, a predicate that returns a reason instead of a boolean,
a loop that repairs against that reason --- has nothing to do with text redaction
specifically. Watch it gate something else entirely: a JSON payload against a small
schema.
""")

code(r"""
def verify_ticket_schema(payload: dict) -> Result:
    if "id" not in payload:
        return Result(False, "missing_field", 'Required field "id" is absent.')
    if payload.get("severity") not in ("low", "medium", "high"):
        return Result(False, "invalid_enum",
                      '"severity" must be low/medium/high, got {!r}.'
                      .format(payload.get("severity")))
    if not isinstance(payload.get("duration_minutes"), int) or payload["duration_minutes"] <= 0:
        return Result(False, "invalid_type",
                      '"duration_minutes" must be a positive integer.')
    return Result(True)


for ticket in [
    {"id": "T-1", "severity": "high", "duration_minutes": 47},   # valid
    {"severity": "high", "duration_minutes": 47},                # missing "id"
    {"id": "T-3", "severity": "urgent", "duration_minutes": 10}, # bad enum value
    {"id": "T-4", "severity": "low", "duration_minutes": -5},    # bad duration
]:
    print(verify_ticket_schema(ticket))
""")

md(r"""
Same shape, different domain: fail on the first violated rule, name which one, say why.

If you picked JSON-schema validation for Exercise 4, you have just watched this cell do
the thing your own predicate does — the resemblance is the point, not a repeat. If you
picked something else, the resemblance is still the point: the four bullets in
Exercise 4 were never four different techniques. They were one technique, naming four
domains where ground truth happens to be available.
""")

md(r"""
---

### Where this shows up in current research

The pattern you just built — a programmatic check gating a generator, with failures fed
back as signal — is the mechanism behind reinforcement learning from verifiable rewards
and the verifier-gated generation loops in recent reasoning systems. See the linked
papers in the accompanying two-page description.

The failure mode you just found shows up there too, and is discussed far less: a
verifiable reward is only as good as the verifier's coverage, and coverage gaps become
optimisation targets the moment a model is trained against them. Section 12 computed
exactly what that means for the gap you found in Section 9 — not a claim to take on
faith, a number you ran.

### Files

- `redaction_task.py` — the reports and their ground truth
- `recorded_generator.py` — recorded model outputs, with the curation documented
- `verifier_reference.py` — reference solutions, plus `KNOWN_GAPS`
- `solutions/` — worked solutions to Exercises 1-3 (Exercise 4 is open-ended by
  design: what it asks for is your own three adversarial cases, not a fixed answer)
""")

nb["cells"] = c
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.9"},
}

with open("01_verifier_as_gate.ipynb", "w") as f:
    nbf.write(nb, f)

print("wrote 01_verifier_as_gate.ipynb ({} cells)".format(len(c)))
