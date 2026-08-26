# SPDX-License-Identifier: MIT
"""Optional: run the loop against a live model instead of the recordings.

Nothing in the notebook requires this. Every exercise completes offline, for free,
using `recorded_generator.py`. This file exists for readers who have an API key and
want to see the repair loop react to feedback it can actually read --- which is the
one thing a recording cannot demonstrate.

    pip install anthropic
    export ANTHROPIC_API_KEY=...        # or: ant auth login

Then, in the notebook:

    from live_generator import LiveGenerator
    gen = LiveGenerator(report)
    text, result, n = repair_loop(report, generator=gen)

Cost note, since a classroom may care: each attempt is a few hundred tokens in and
out. A full pass over all four reports is a fraction of a cent. It is still not free,
which is why it is not the default path.
"""

import os
from typing import Optional

REDACTION_PROMPT = """\
Rewrite the incident report below for public publication.

Remove every direct identifier: names, badge numbers, ticket IDs.
Keep every operational fact: durations, counts, timestamps, dates.
Do not add information that is not in the original.

Return only the rewritten report, with no preamble.

REPORT:
{text}"""

REPAIR_PROMPT = """\
Your rewrite did not pass verification.

{feedback}

Here is the report you were given:

{original}

And here is your rewrite:

{attempt}

Return only a corrected rewrite, with no preamble."""


class LiveGenerator:
    """Same call signature as RecordedGenerator, backed by a real API call.

    Because it is interface-compatible, `repair_loop` does not need to know which
    one it is driving --- which is worth pointing out to learners as a small lesson
    in its own right about where to put a seam.
    """

    def __init__(self, report, model: str = "claude-opus-5",
                 client=None) -> None:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "The live path needs the anthropic package: pip install anthropic. "
                "The notebook does not require it --- use RecordedGenerator instead.")

        if client is None and not (os.environ.get("ANTHROPIC_API_KEY")
                                   or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            # An `ant auth login` profile also works, so this is a warning rather
            # than an error: the zero-arg client may still resolve credentials.
            print("Note: no ANTHROPIC_API_KEY in the environment. Falling back to "
                  "whatever credentials the SDK can resolve (e.g. an `ant auth "
                  "login` profile).")

        self.report = report
        self.model = model
        self.client = client or anthropic.Anthropic()
        self._last_attempt: Optional[str] = None
        self.calls = 0

    def __call__(self, feedback: str = "") -> str:
        import anthropic

        if feedback and self._last_attempt is not None:
            prompt = REPAIR_PROMPT.format(feedback=feedback,
                                          original=self.report.text,
                                          attempt=self._last_attempt)
        else:
            prompt = REDACTION_PROMPT.format(text=self.report.text)

        try:
            response = self.client.messages.create(
                model=self.model,
                # Deliberately small: the output is one short paragraph, and this is
                # a teaching script that a reader may run in a loop.
                max_tokens=4096,
                # A rewrite of one paragraph does not need deep reasoning, and low
                # effort keeps the cost of running these materials near zero.
                output_config={"effort": "low"},
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Authentication failed. Set ANTHROPIC_API_KEY, or run `ant auth "
                "login`, or just use RecordedGenerator --- the notebook is designed "
                "to work without a key.")
        except anthropic.RateLimitError as exc:
            retry_after = exc.response.headers.get("retry-after", "60")
            raise RuntimeError(
                "Rate limited; retry after {}s.".format(retry_after))
        except anthropic.APIStatusError as exc:
            raise RuntimeError("API error {}: {}".format(exc.status_code, exc.message))
        except anthropic.APIConnectionError:
            raise RuntimeError("Could not reach the API. Check your connection.")

        if response.stop_reason == "refusal":
            raise RuntimeError(
                "The model declined this request. Nothing here should trigger that; "
                "if it does, please report it --- and use RecordedGenerator meanwhile.")

        text = "".join(b.text for b in response.content if b.type == "text").strip()
        self._last_attempt = text
        self.calls += 1
        return text
