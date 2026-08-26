# SPDX-License-Identifier: MIT
"""A stand-in generator that replays recorded model outputs.

Every exercise in these materials runs offline and costs nothing. The outputs below
were produced by prompting a model to redact the reports in `redaction_task.py`,
then curated: we kept the attempts that fail in *instructive* ways and wrote a few
more by hand to make specific failure modes reachable on demand.

That curation is deliberate and worth stating plainly to learners. These are not a
random sample of model behaviour, and nothing here should be read as a benchmark
result. They are teaching fixtures --- chosen so that the verifier you write has
something interesting to catch, and something interesting to *miss*.

The live-API path is in `live_generator.py`, entirely optional.
"""

from typing import Dict, List

# Each attempt is one turn of a generate -> verify -> repair loop. Attempt 0 is the
# first response to the redaction prompt; later attempts are responses to a repair
# prompt carrying the verifier's structured reason.
RECORDED: Dict[str, List[str]] = {
    "INC-001": [
        # Attempt 0: drops the full name, forgets the bare surname. Caught easily.
        "On 14 March 2024, an analyst (badge 88431) reported that the payments server "
        "was unavailable for 47 minutes, affecting 1204 transactions. Costa escalated "
        "to the infrastructure team at 09:12.",
        # Attempt 1: surname gone, badge still there. Caught.
        "On 14 March 2024, an analyst (badge 88431) reported that the payments server "
        "was unavailable for 47 minutes, affecting 1204 transactions. The analyst "
        "escalated to the infrastructure team at 09:12.",
        # Attempt 2: clean. Passes, and deserves to.
        "On 14 March 2024, an analyst reported that the payments server was "
        "unavailable for 47 minutes, affecting 1204 transactions. The analyst "
        "escalated to the infrastructure team at 09:12.",
    ],
    "INC-002": [
        # Attempt 0: identifiers gone -- but "96 files" went with them. The redaction
        # succeeded and the report became useless. This is why the predicate has two
        # halves.
        "A ticket was opened at 22:40 after the nightly batch job failed 3 times in a "
        "row. An engineer restarted the job manually; it completed in 18 minutes.",
        # Attempt 1: fact restored, identifiers still gone.
        "A ticket was opened at 22:40 after the nightly batch job failed 3 times in a "
        "row. An engineer restarted the job manually; it completed in 18 minutes and "
        "processed 96 files.",
    ],
    "INC-003": [
        # Attempt 0: initials. A literal-substring verifier sees no identifier and
        # passes it. In a team with one Lindqvist, "T.L." identifies him exactly.
        "During the 12 June 2024 migration window, engineer T.L. (badge redacted) "
        "observed replication lag of 210 seconds across 4 shards. The lag cleared "
        "without intervention after 35 minutes.",
        # Attempt 1: initials gone, but now a definite description that singles out
        # one person just as well. Still passes a literal verifier.
        "During the 12 June 2024 migration window, the only Swedish engineer on the "
        "migration crew observed replication lag of 210 seconds across 4 shards. The "
        "lag cleared without intervention after 35 minutes.",
        # Attempt 2: genuinely clean.
        "During the 12 June 2024 migration window, an engineer observed replication "
        "lag of 210 seconds across 4 shards. The lag cleared without intervention "
        "after 35 minutes.",
    ],
    "INC-004": [
        # Attempt 0: badge literal removed, but restated as a range that still
        # contains it ("18402"). A literal verifier catches this one -- it is here
        # to make attempt 1's false alarm land right after a genuine catch.
        "At 03:05, the on-call engineer acknowledged the alert within 2 minutes. The "
        "root cause was a misconfigured retry policy that generated 18400 duplicate "
        "requests over 26 minutes. The engineer's badge, in the 18402 range, appears "
        "in the audit log next to each retry.",
        # Attempt 1: badge gone for real -- but the count is now written with a
        # thousands separator. A naive verifier reports the essential fact as LOST and
        # sends this back for repair. It is a false alarm: nothing was lost.
        "At 03:05, the on-call engineer acknowledged the alert within 2 minutes. The "
        "root cause was a misconfigured retry policy that generated 18,400 duplicate "
        "requests over 26 minutes. The badge appears in the audit log next to each "
        "retry.",
        # Attempt 2: clean, and formatted the way the naive verifier expects.
        "At 03:05, the on-call engineer acknowledged the alert within 2 minutes. The "
        "root cause was a misconfigured retry policy that generated 18400 duplicate "
        "requests over 26 minutes. The badge appears in the audit log next to each "
        "retry.",
    ],
}


class RecordedGenerator:
    """Replays recorded attempts, one per call, mimicking a repair loop.

    The verifier's feedback is accepted and ignored --- a recording cannot react to
    it. That is a real limitation of teaching this offline, and the notebook says so
    where it matters. What the fixtures preserve faithfully is the *shape* of the
    loop: each successive attempt is what a model actually tends to do after being
    told which rule it broke.
    """

    def __init__(self, report_id: str) -> None:
        self.report_id = report_id
        self._attempts = RECORDED[report_id]
        self._calls = 0

    def __call__(self, feedback: str = "") -> str:
        """Return the next recorded attempt. `feedback` is accepted for interface
        parity with a live generator, and deliberately unused.

        Defining `__call__` is what lets `generator(feedback)` work as if
        `generator` were a plain function, even though it is an object that
        remembers how many attempts it has already handed out."""
        if self._calls >= len(self._attempts):
            raise RuntimeError(
                "No recorded attempt {} for {}. The recordings run out on purpose: a "
                "repair loop needs an iteration cap, and hitting the end of the tape "
                "is a good moment to notice that.".format(self._calls, self.report_id)
            )
        attempt = self._attempts[self._calls]
        self._calls += 1
        return attempt

    @property
    def calls(self) -> int:
        return self._calls
