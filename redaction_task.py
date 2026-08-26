# SPDX-License-Identifier: CC-BY-4.0
"""The task the learner will gate: redacting incident reports for publication.

An operations team wants to publish its incident write-ups. Each report must lose
its direct identifiers (names, badge numbers, internal ticket IDs) and keep every
operational fact (durations, counts, timestamps) --- those are the whole point of
publishing.

That is two constraints pulling in opposite directions, and both are decidable in
code: we know exactly which strings must vanish and which must survive. This module
holds only the data. The predicate that decides it is what the learner writes.

Written for the NeurIPS 2026 Education Track. Runs offline; no API key needed.
Every report, name, and fact below is invented for this lesson; none refers to a
real person or a real incident.
"""

from typing import Dict, List, NamedTuple


class Report(NamedTuple):
    """One incident report, with its ground truth attached.

    The ground truth is what makes deterministic verification possible here. We are
    not asking a model to guess which words were identifying --- we already know.
    """

    report_id: str
    text: str
    identifiers: List[str]  # must NOT survive redaction
    essential_facts: List[str]  # must survive redaction
    note: str = ""


REPORTS: List[Report] = [
    Report(
        report_id="INC-001",
        text=(
            "On 14 March 2024, analyst Mariana Costa (badge 88431) reported that the "
            "payments server was unavailable for 47 minutes, affecting 1204 "
            "transactions. Costa escalated to the infrastructure team at 09:12."
        ),
        identifiers=["Mariana Costa", "Costa", "88431"],
        essential_facts=["14 March 2024", "47 minutes", "1204", "09:12"],
    ),
    Report(
        report_id="INC-002",
        text=(
            "Ticket OPS-5510 was opened by Priya Raman at 22:40 after the nightly "
            "batch job failed 3 times in a row. Raman restarted the job manually; it "
            "completed in 18 minutes and processed 96 files."
        ),
        identifiers=["Priya Raman", "Raman", "OPS-5510"],
        essential_facts=["22:40", "3 times", "18 minutes", "96 files"],
    ),
    Report(
        report_id="INC-003",
        text=(
            "During the 12 June 2024 migration window, engineer Tomas Lindqvist "
            "(badge 21007) observed replication lag of 210 seconds across 4 shards. "
            "The lag cleared without intervention after 35 minutes."
        ),
        identifiers=["Tomas Lindqvist", "Lindqvist", "21007"],
        essential_facts=["12 June 2024", "210 seconds", "4 shards", "35 minutes"],
    ),
    Report(
        report_id="INC-004",
        text=(
            "At 03:05, on-call engineer Yuki Tanaka acknowledged the alert within 2 "
            "minutes. The root cause was a misconfigured retry policy that generated "
            "18400 duplicate requests over 26 minutes. Tanaka's badge, 18402, appears "
            "in the audit log next to each retry."
        ),
        identifiers=["Yuki Tanaka", "Tanaka", "18402"],
        essential_facts=["03:05", "2 minutes", "18400", "26 minutes"],
        note=(
            "Deliberate trap: badge 18402 and the count 18400 differ by 2 and share "
            "a four-digit prefix. A substring-based verifier will get this wrong in a "
            "way that is easy to miss."
        ),
    ),
]

REPORTS_BY_ID: Dict[str, Report] = {r.report_id: r for r in REPORTS}
