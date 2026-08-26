# Facilitator guide

For instructors running `01_verifier_as_gate.ipynb`. This is not a piloted document —
no classroom has run these materials yet — but it is not a guess either: the timing and
stall points below come from actually building and re-testing the notebook, including
one pass where an agent worked through it cold, as a stand-in for the target learner,
and got stuck at four specific points before the material was fixed under it. Treat this
as informed, not validated. If you run a session, the single most useful thing you can
do for the next instructor is correct this document against what actually happened.

## Timing, section by section

These are per-section estimates for an advanced-undergraduate audience with the stated
prerequisites (Python functions/strings/lists, a rough idea of what an API call is).
Add time for a slower group; do not plan to compress it further.

| Section | What happens | Estimate |
|---|---|---|
| 1–3 | Task framing, why not an LLM judge, the decidability condition | 8–10 min |
| 4 (Ex. 1) | Write `verify`, returning a reason not a boolean | 12–15 min |
| 5 (Ex. 2) | Close the repair loop, with an iteration cap | 8–10 min |
| 6 | Run the verifier over INC-003, guess the leak, find the T.L. miss | 6–8 min |
| 7 (Ex. 3) | Extend the verifier: number normalisation + initials guard | 15–20 min |
| 8 | The extension's own false alarm (IT / ASAP) | 5 min |
| 9 | The definite-description gap that does not close | 5–7 min |
| 10 | Restoring decidability by adding a fact (knowledge-based check) | 5 min |
| 11 | What a verifier actually buys you | 3–5 min |
| 12 | Scoring recorded attempts as a reward (RLVR connection) | 5–7 min |
| **Subtotal, Sections 1–12** | | **~75–90 min** |
| 13 (Ex. 4) | Learner's own gate: predicate, 3 adversarial cases, defense | **45+ min** |
| 14 | The same predicate shape gates a JSON payload (read-only, no exercise) | 3–5 min |

**Do not schedule Exercise 4 in the same block as Sections 1–12** unless the session is
at least two hours with a break. It works better as a second session, office-hours
follow-up, or take-home; the rubric (`03_rubric_exercise_4.md`) is written to be gradable
asynchronously. Section 14 comes after Exercise 4 on purpose — it reapplies the same
predicate shape to a JSON payload, and reading it before the learner has committed to
their own domain would hand them a worked answer for one of Exercise 4's four suggested
domains instead of a generalisation to notice afterward.

The ~90-minute figure on the notebook's first cell describes Sections 1–12 only, not the
whole notebook. If you are quoting a single number to a class, say "about 80 minutes,
plus a 45-minute exercise to do afterward" rather than "90 minutes."

## Where learners are likely to stall

The first four were found by walking the notebook cold and confirmed by re-running the
actual functions afterward. The underlying bugs are fixed, but the concepts that caused
them are still genuinely difficult, so expect learners to pause at the same spots even
though the notebook no longer breaks there. The fifth is a different kind of risk,
caught by review rather than by a cold walkthrough: not a place learners get stuck, but
a place they can skip past without noticing.

1. **Section 7's self-check only exercises half of `verify_v2`.** The first
   self-test loop iterates `INC-003`, which tests the initials guard but never
   exercises number normalisation — a learner can leave that half broken and see
   green output. The notebook now runs both `INC-003` and `INC-004` in that loop with
   a note pointing at which line reveals the bug if normalisation is wrong. Still
   worth a live check: ask a learner mid-exercise which report their last test run
   used, and whether they tried the other one.
2. **Regex lookahead/lookbehind, introduced as an optional aside.** The exercise's
   *direct* path (`text.replace(",", "")`) needs no regex at all; the general regex
   version is presented as a documented but non-required alternative. Learners who
   reach for regex first anyway (a common reflex) will spend real time here. Steer
   them to the direct path first if the session is time-boxed.
3. **`NamedTuple` with `Optional` and default values, used from Section 4 on.**
   A one-line comment explains it at first use, but learners without recent exposure
   to `typing` may still need a verbal example (`result.rule` vs. `result[1]`).
4. **Import fails outside `materiais/`.** If Jupyter is launched from the repository
   root or the user's home directory, the first code cell now raises a clear
   `ModuleNotFoundError` with instructions rather than a bare traceback — but confirm
   at the start of the session that everyone's working directory is right before
   anyone hits Section 1, since this is the kind of thing that eats ten minutes per
   affected learner if caught late.
5. **Section 6's diagnosis is one cell away from the reveal.** After running the
   verifier over the three `INC-003` attempts, the very next cell explains which one
   leaks and why. In a linearly-read notebook that means a learner can go straight from
   "all three pass" to the answer without ever forming a guess — the one Bloom
   objective this exercise is meant to back ((Analyze) locate a false negative and
   characterize the format) ends up narrated rather than exercised. There is now a
   one-line prompt between the two cells asking for a written guess before reading on;
   in a live session, make it a real pause — ask learners to say their guess out loud,
   or drop it in chat, before you advance the slide or let them scroll further. If a
   learner in a synchronous session gets to the reveal cell before committing to a
   guess, treat it the same as skipping ahead in a reading — worth a friendly nudge
   back, not a hard rule.

## Common misconceptions to watch for

- **"The verifier is broken" (Section 6).** It is not; it does exactly what was
  written. The miss is a scope question, not a bug. If a learner wants to "fix" it
  by making the string match fuzzier, that is a reasonable instinct to redirect
  toward Section 7 rather than shut down.
- **"We should just add a rule for every case we can think of" (Sections 8–9).**
  This is the instinct the material is built to interrupt. Section 8 is there
  specifically so this instinct gets tested against a real, not hypothetical,
  consequence (a rule that helps also hurts) before Section 9 asks for a considered
  answer.
- **"Ex. 4's ground truth turned out not to exist for my domain."** This is not a
  failure state — see the note added to `03_rubric_exercise_4.md`. Some learners will
  pick a domain (a "clean writing" checker, a "polite tone" checker) where the
  constraint is not actually decidable in code, and discovering that mid-exercise is
  one of the most valuable outcomes the exercise can produce. Do not let a learner
  who hits this conclude they did the exercise wrong.

## For your first live tester

If you are running this with one person before a full session (recommended — this is
exactly the pass these materials have not had yet), a few concrete things to note as
they go, beyond "did they finish":

- Where did they pause without asking a question — silence can mean either "thinking"
  or "stuck," and only they can tell you which after the fact.
- Did Section 8's IT/ASAP result feel like a bug to them, or did the text land as
  intended (an honest limitation, not broken code)? This is the section most likely to
  read as flaky if the framing does not land.
- Did they reach for regex before reading that the exercise does not need it
  (misconception #2 above)?
- How long did Exercise 4 actually take them, and did they attempt it in the same
  sitting as the rest?

There is no fixed feedback form for this — a few sentences per point above, sent back
however is convenient, is enough to correct the timing table and stall list against a
real run instead of a build-time guess.
