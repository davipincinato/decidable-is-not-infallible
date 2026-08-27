# Rubric — Exercise 4 ("your own gate")

For instructors grading the open-ended exercise. The domain is chosen by the learner
(unit tests, a JSON schema, a summary, a translation, or anything else with ground
truth available), so this rubric grades the *reasoning*, not a fixed answer.

Four criteria, 0–2 points each, 8 total.

| # | Criterion | 0 | 1 | 2 |
|---|---|---|---|---|
| 1 | **Predicate** returns a structured reason, not a boolean | Boolean only, or crashes on a valid input | Returns a reason, but it is generic ("failed") | Reason names the specific rule violated, usable as repair feedback |
| 2 | **Three adversarial inputs**, written *before* testing | Fewer than three, or evidently written after seeing results | Three inputs, but at least one is a trivial restatement of the obvious case | Three genuinely distinct near-misses that each probe a different assumption of the predicate |
| 3 | **Results reported** for all three | Missing, or contradicted by re-running the code | All three reported and correct | All three reported, and a surprising outcome (accepted when expected to reject, or vice versa) is called out |
| 4 | **Defends** extend-vs-document | No justification, or restates the decision without reasoning | Justification given, but does not weigh coverage against cost | Explicitly weighs the coverage gained by extending against the complexity cost, tied to the specific gap found in step 3 |

**Reading the total.** 6–8: objectives 5 and 6 met. 3–5: the mechanics are there but the
judgment call is thin — worth a follow-up question in office hours. 0–2: revisit
exercise 3 before attempting this one.

## When the learner discovers there is no ground truth

Some learners will pick a domain — a "clean writing" checker, a "polite tone" checker,
a constraint that turns out to be a matter of taste rather than fact — and discover
partway through that the property they chose is not actually decidable in code the way
the redaction task was. **This is not a failure of criterion 3** ("results reported");
it is arguably the exercise working as intended, one level up. Do not penalize an empty
or negative results section that comes from this discovery.

Instead, redirect it to criterion 4. A learner who writes "I chose X, believed it was
decidable, and found no fact in my input that actually pins it down — here is why, and
here is what I would need to add for it to become decidable" has done the Section 10--11
move for their own domain, unprompted, and should score at the top of criterion 4 for
it. The only thing to check is that they actually located *why* it is not decidable
(what fact is missing, and where it would have to come from), not just that they gave
up on finding a predicate.

## Honest note on this rubric

This is the simplest version: criteria in prose, not calibrated against any actual
student submission — there is no batch of real answers to check it against yet.
Exercise 4 is open-ended by design (the domain is the learner's choice), so an
instructor's judgment will still carry weight applying these criteria case by case.
Treat this as a first pass, meant to be tightened after it meets real answers, not as
a finished instrument.
