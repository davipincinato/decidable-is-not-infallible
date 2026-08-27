# Facilitator guide

For instructors running `01_verifier_as_gate.ipynb`. Not a classroom pilot yet, but no
longer a pure build-time guess either: two real people have now run the notebook cold
(n=2, reported finding by finding under "Real tester feedback" below), on top of an earlier pass
where an agent worked through it as a stand-in for the target learner and got stuck at
four specific points before the material was fixed under it. Both testers were
recruited informally (people available to the author, not a classroom, not sampled
from the module's stated target population under session conditions). Treat this as
informed by two real, self-reported data points, not validated by a classroom. If you
run a session, the single most useful thing you can do for the next instructor is
correct this document against what actually happened.

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
| 9 | Auditing systematically: misses (casing/whitespace/invisible chars fixed, look-alikes disclosed), then false alarms and the collision sweep | 12–15 min |
| 10 | The definite-description gap that does not close | 5–7 min |
| 11 | Restoring decidability by adding a fact (knowledge-based check) | 5 min |
| 12 | What a verifier actually buys you | 3–5 min |
| 13 | Scoring recorded attempts as a reward (RLVR connection) | 5–7 min |
| **Subtotal, Sections 1–13** | | **~84–107 min** |
| 14 (Ex. 4) | Learner's own gate: predicate, 3 adversarial cases, defense | **45+ min** |
| 15 | The same predicate shape gates a JSON payload — and hits its own false negative (no exercise, but not passive) | 6–8 min |

**Do not schedule Exercise 4 in the same block as Sections 1–13** unless the session is
at least two hours with a break. It works better as a second session, office-hours
follow-up, or take-home; the rubric (`03_rubric_exercise_4.md`) is written to be gradable
asynchronously. Section 15 comes after Exercise 4 on purpose — it reapplies the same
predicate shape to a JSON payload, and reading it before the learner has committed to
their own domain would hand them a worked answer for one of Exercise 4's four suggested
domains instead of a generalisation to notice afterward. It is also no longer a
read-only demo: the section now runs the JSON verifier into its own false negative (a
`low`-severity ticket running three days passes every field rule, because no rule
relates two fields to each other), which is the redaction arc's `T.L.` moment in a
domain that shares no code with it. If a session runs out of time, this is a defensible
thing to assign as reading — but do not cut it entirely, because it is the only place
the notebook shows that the gap belongs to writing predicates rather than to matching
text.

**One caveat if you do assign it as standalone reading.** A reader who came to this
section without the earlier ones reported that the ticket false negative did *not*
read as the same problem they had seen before — which is unsurprising, since they had
not seen it. The section's punch depends on recognising `T.L.`, the Section 10 gap and
the Section 12 sentence, and it used to name all three without recalling any of them.
Each back-reference now carries a one-clause reminder of what it refers to, so the
section stands on its own. That fix has not been re-tested. This matters beyond
skimmers: because Exercise 4 is meant to be a separate session, even a diligent
learner meets Section 15 potentially days after Section 7, with those references
cold.

The ~90-minute figure on the notebook's first cell describes Sections 1–13 only, not the
whole notebook. If you are quoting a single number to a class, say "about 90 minutes,
plus a 45-minute exercise to do afterward" rather than "90 minutes" on its own.
Section 15 (6–8 min) comes after that exercise and is in neither figure; the whole
notebook, end to end, is 135–160 min.

**Real data (n=2):** tester 1 finished Sections 1–13 in **52 minutes** and Exercise 4
in **~40 minutes**; tester 2 (CS student) finished the whole notebook, Sections 1–13
plus Exercise 4, in **~35 minutes**, with Exercise 4 alone at **~30 minutes**. Those
two figures cannot both describe the whole notebook — they would leave five minutes for
Sections 1–13 — and the tester was not asked to disambiguate. The likely reading is 35
min for Sections 1–13 *plus* 30 for Exercise 4, which is consistent with tester 1's 52
+ 40. Treat the pair as one loosely-reported session, not as two measurements.

Either way both testers came in well under the estimates above. Two data points still
do not replace the table (self-paced, highly focused individual reading alone is not
the same population as a classroom with questions and discussion), but both point the
same direction: the
estimate above likely runs high for a fast, motivated solo learner, and the Exercise 4
skeleton added after tester 1 (see finding 6 below) may be shaving real time off the
blank-page problem (40 min → 30 min), though n=2 is too small to call that confirmed.
Report your own numbers here rather than trusting either figure blindly.

Note that both testers ran a **shorter Section 9** than the one that ships now: the
false-alarm half and the collision sweep were added afterward, in response to a
reviewer finding a false alarm the section had never tested for. Add roughly 6 minutes
to both reported times before comparing them to the table.

## Where learners are likely to stall

The first four were found by walking the notebook cold and confirmed by re-running the
actual functions afterward. The underlying bugs are fixed, but the concepts that caused
them are still genuinely difficult, so expect learners to pause at the same spots even
though the notebook no longer breaks there. The fifth is a different kind of risk,
caught by review rather than by a cold walkthrough: not a place learners get stuck, but
a place they can skip past without noticing. The sixth came from a real tester, the
seventh from a reviewer.

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
   them to the direct path first if the session is time-boxed. **This one has been
   through two failed fixes and is worth understanding before you run a session.**
   After tester 1 ("didn't know what regex was") a line was added directly above the
   paragraph: *"if you have never used regex, skip this paragraph."* Tester 2 read it
   anyway — and knew regex perfectly well: *"the word regex pulled my attention before
   I processed the warning."* Two testers, two opposite causes, same outcome. The line
   failed because it treated a **placement** problem with an **instruction**: a written
   "skip this" helps neither the person who is curious because they don't know, nor the
   person whose attention was captured before they reached the warning. There is now a
   prominent callout at the very top of Section 7, before the exercise begins, that
   states the exercise needs no regex and reports that both testers lost time there.
   **Untested.** If it fails a third time, the honest move is to stop patching and
   either move the paragraph after the exercise or cut it — and note that a live verbal
   steer has worked every time the written word has not.
3. **`NamedTuple` with `Optional` and default values, used from Section 4 on.**
   A one-line comment explains it at first use, but learners without recent exposure
   to `typing` may still need a verbal example (`result.rule` vs. `result[1]`).
4. **Import fails outside the folder these files are in.** If Jupyter is launched
   from the repository root or the user's home directory, the first code cell raises a
   `ModuleNotFoundError` with instructions rather than a bare traceback — but confirm
   at the start of the session that everyone's working directory is right before
   anyone hits Section 1, since this is the kind of thing that eats ten minutes per
   affected learner if caught late.
5. **Section 6's diagnosis is one cell away from the reveal.** After running the
   verifier over the three `INC-003` attempts, the cell after next explains which one
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
6. **Exercise 4 was the hardest part for our first real tester, and not for a Bloom
   reason.** The difficulty was not judgment (extend-vs-document) or even picking a
   domain — it was staring at a blank cell with no code to start typing into. The
   exercise now ships a `verify_mine` skeleton and a one-line ground-truth hint per
   suggested domain (see Section 14). Tester 2 used the skeleton, picked the
   number-based domain from the suggested list, and finished in ~30 minutes (down from
   tester 1's ~40) without reporting the same blank-page difficulty — a real but
   single-step-removed signal that the skeleton helps, not a controlled comparison. If
   a learner still stalls here, the failure mode to watch for is "I don't know how to
   start," not "I don't understand what's being asked" — the fix for the first is a
   nudge toward the skeleton; the fix for the second is a conversation about the
   concept.
7. **Section 9's second half asks learners to accept that the notebook's own audit
   was wrong.** The section now runs a mirror-image checklist (clean text that should
   pass) after the original one (leaks that should be caught), and one row fails: a
   redaction with no identifier in it is rejected because the surname `Raman` collides
   with `Raman spectroscopy`. The pedagogical risk is not confusion about the
   collision — that reads clearly — it is the 2×2 grid that follows, which says the
   audit tested three of its four cells and called itself complete. Some learners read
   that as the authors being careless; the point is the opposite, and worth saying out
   loud: the checklist and the blind spot came from the same person, which is a
   structural limit, not a personal lapse. That is the whole argument for the
   collision sweep in `check_materials.py`, and it lands or fails on this framing. If
   you only have time to add one sentence of your own to this section, add that one.

- **"The verifier is broken" (Section 6).** It is not; it does exactly what was
  written. The miss is a scope question, not a bug. If a learner wants to "fix" it
  by making the string match fuzzier, that is a reasonable instinct to redirect
  toward Section 7 rather than shut down.
- **"We should just add a rule for every case we can think of" (Sections 8–10).**
  This is the instinct the material is built to interrupt. Section 8 tests it against
  a real, not hypothetical, consequence (a rule that helps also hurts); Section 9
  turns it into a checklist with an explicit fix-or-disclose call made for each item,
  not just for one, and then shows the checklist itself missing a whole category;
  Section 10 asks for a considered answer on the one gap that has no fix at all.
- **"So the answer is to write a more careful checklist" (Section 9).** The most
  likely wrong lesson from the 2×2 grid. A more careful checklist is still bounded by
  what its author thought of; the section's actual claim is that the way past that is
  a check that enumerates instead of remembering (the collision sweep), not more
  diligence. If a learner proposes a longer checklist, that is the right moment to ask
  what would have to be true for them to know it was complete.
- **"Ex. 4's ground truth turned out not to exist for my domain."** This is not a
  failure state — see the note added to `03_rubric_exercise_4.md`. Some learners will
  pick a domain (a "clean writing" checker, a "polite tone" checker) where the
  constraint is not actually decidable in code, and discovering that mid-exercise is
  one of the most valuable outcomes the exercise can produce. Do not let a learner
  who hits this conclude they did the exercise wrong.

## Real tester feedback (n=2)

Two people have run the notebook cold. Kept here in full, tester by tester, because
each new tester's report should be added the same way, not used to overwrite the last.
This is the synthesized, per-finding version; the authors keep the raw verbatim Q&A
separately, and it is deliberately not shipped with these materials.

### Tester 1

1. **Where they paused without asking.** Regex ("didn't know what it was"); the
   README (it referenced a folder name that turned out to be Portuguese — see below);
   Exercise 4 ("hard to do something from scratch, with no context, no ideas").
2. **Section 8's IT/ASAP framing.** "At first it seemed like a bug. The text
   afterward made it clearer, but it left a bit of doubt." This is exactly the risk
   this guide flagged before anyone had tested it — confirmed, not hypothetical. A
   one-line warning was added before the code cell in Section 8 ("one of the two
   calls below will look wrong... it is not") to front-load the framing instead of
   only explaining after the fact.
3. **Reached for regex.** Yes — "because it was talking about regex," i.e. the
   optional paragraph's mere presence pulled them in even though the exercise does
   not need it. An explicit "if you have never used regex, skip this paragraph" line
   was added directly above it — which then failed against tester 2 for the opposite
   reason. See stall item 2 for the full history and what replaced it.
4. **Timing.** 52 min for Sections 1–13; ~40 min for Exercise 4 alone, "mostly
   because of a lot of difficulty getting started from zero" — matches point 1.
   Addressed the same way as point 1's Exercise 4 finding: see item 6 above.

**One finding tester 1's four questions did not anticipate, and the most concrete fix
to come out of that round:** the README referenced the folder these files live in by a
name that was still in Portuguese (`materiais`, left over from this project's internal
working language) rather than English, in a resource meant for an English-speaking,
international audience. Fixed: the folder is now named `materials/`, and every
reference to it in the README, the facilitator guide, and the notebook's import-error
message was reworded to not hard-code a folder name at all (so it stays correct
whether someone unzips the package, clones the repo, or downloads a GitHub zip
archive, each of which produces a differently-named folder). Worth an explicit
proofreading pass for language leakage on any resource whose authors work day-to-day
in a language other than the one it is written in — spellcheck does not catch a
correctly-spelled word in the wrong language.

### Tester 2 (CS student) — after tester 1's four fixes

Ran against the "For your next live tester" list below, which tester 1's round left
open.

1. **Where they paused without asking.** Three spots, and only one is a problem: the
   regex aside (tried it anyway despite the skip line — see below); Section 6's
   "write your guess before reading on" prompt (paused for real, did not scroll past
   it) — this is the exercise *working as intended*, not a stall, since the whole
   point of that prompt is to force a real pause before the reveal; and the start of
   Exercise 4, deciding which domain to pick before touching the `verify_mine`
   skeleton (picked the number-based domain from the suggested list — "it's where I
   function best," a normal decision pause, not a blank-page stall).
2. **Section 8's IT/ASAP framing — the lead-in fix worked.** "The warning that was
   already added to the cell before ('one of the two calls below will look wrong...
   it is not') arrived first, so I already expected it — the doubt tester 1 reported
   was much smaller for me because of that warning." First confirmation that this fix
   holds under a second, independent run.
3. **Reached for regex anyway — the skip-line fix did not stop it.** Read the aside
   despite the line, but for a different reason than tester 1: not "didn't know what
   regex was" (they know it well) but "the word regex pulled my attention before I
   processed the skip instruction." Same outcome as tester 1, different mechanism —
   see the added note under "Where learners are likely to stall" item 2 above. The
   written line alone is not reliable; a live verbal steer is.
4. **Exercise 4 timing.** Did it in the same session as the rest (against the guide's
   own recommendation), ~30 minutes, no reported blank-page difficulty — down from
   tester 1's ~40 minutes with the same complaint. Consistent with, but not proof of,
   the `verify_mine` skeleton helping (see the timing table note above).
5. **Total notebook time and error rate (a question tester 1 wasn't explicitly asked).**
   ~35 minutes end to end, single continuous session, zero `ModuleNotFoundError` and
   zero unexpected results across Sections 4–13 — nothing broke on a second cold run.

No language-leakage issues reported this round (the folder-rename fix from tester 1
was already in place for this run).

## For your next live tester

What is now confirmed vs. still open, after two rounds plus one re-read pass:

- **Confirmed working:** the Section 8 lead-in (2 for 2 — reduces but does not fully
  eliminate the "is this a bug" reaction); the folder-name English fix (no
  language-leakage reports on the second run).
- **Confirmed broken twice, now on its third attempt:** learners read the optional
  regex paragraph regardless (2 for 2, for opposite reasons). The inline "skip this
  paragraph" line failed; it has been replaced by a prominent callout at the top of
  Section 7, before the exercise starts, which also tells the learner that both prior
  testers lost time there. **If this fails a third time, stop patching the wording** —
  move the paragraph after the exercise, or cut it. A live verbal steer has worked
  every time the written word has not, so in a time-boxed session, say it out loud.
- **Suggestive, not confirmed:** the `verify_mine` skeleton may be cutting Exercise 4
  time (tester 1: ~40 min with blank-page complaints; tester 2: ~30 min, no such
  complaint) — n=2 is too small to call this settled.
- **Not yet tested:** Section 9's encoding-look-alike disclosure carries the same
  "looks like a bug" framing risk as Section 8 did, one section later, and has no
  lead-in warning yet. Watch for the same reaction there.
- **Confirmed working, from two directions:** the 2×2 audit grid in Section 9 reads as
  intended — as authors finding a structural limit and owning it, not as authors having
  been careless, which was the specific risk this section was flagged for (stall item
  7). Both original testers re-read Sections 7–9 and signed off; separately, a reader
  who opened *only* Sections 9 and 15, with none of the buildup, was asked what they
  made of the grid and said, unprompted, that the authors "found a structural limit and
  owned it." The second is the stronger evidence: the framing survives even without the
  Section 8 false alarm to prepare it. That same reader also confirmed the collision
  sweep's purpose was clear on its own.
- **Still genuinely untested:** a first-time learner reading the notebook *linearly*,
  start to finish, meeting Section 9's admission in the flow the material was written
  for. Every reader so far has either re-read it knowing the material or jumped
  straight to it. Also untested: whether learners connect the sweep to their own
  Exercise 4 without being told.
- Any word, path, or reference that reads as written by someone thinking in a
  different language than English — worth an explicit check every round, even after a
  clean run, since it is the kind of thing a native speaker of the material's working
  language will not notice on their own re-read.

There is no fixed feedback form for this — a few sentences per point above, sent back
however is convenient, is enough to correct this document against another real run.
