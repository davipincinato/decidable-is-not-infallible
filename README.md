# Decidable is not infallible

### Teaching materials — NeurIPS 2026 Education Track

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22126691.svg)](https://doi.org/10.5281/zenodo.22126691)

Permanent, citable archive: [doi.org/10.5281/zenodo.22126691](https://doi.org/10.5281/zenodo.22126691)
--- the concept DOI, which always resolves to the newest version.
Live development repo: [github.com/davipincinato/decidable-is-not-infallible](https://github.com/davipincinato/decidable-is-not-infallible).

A self-contained lesson on **deterministic verification as a generation gate**: the
pattern where a program, not a judge model, decides whether a language model's output
is acceptable, and its failure message drives the retry. ~90 minutes for the exercises
and discussion; Exercise 4 is open-ended and typically needs 45+ minutes more — see
`02_FACILITATOR_GUIDE.md` for the per-section breakdown.

The learner builds the loop, then finds the output it wrongly accepts.

## Run it

1. **Check you have Python 3.9 or newer.** Everything here is tested on 3.9.6;
   nothing needs a newer feature, but nothing below 3.9 has been tried.
   ```bash
   python3 --version
   ```

2. **Get the files and open a terminal in the folder this README lives in** — unzip
   the package, or clone the repo, then `cd` into whichever folder that produced.

3. **Run the regression check.** No installation needed — it only uses the standard
   library.
   ```bash
   python3 check_materials.py
   ```
   Expected: every claim line starts with `[ok  ]` (section headings and the
   collision- and fact-sweep report lines are not claims), and the last line reads
   `All claims hold.`
   If something fails here, stop and fix the environment before opening the notebook —
   the notebook assumes this passes.

4. **Open the notebook.** Use whichever of these two you already have; you only need
   one.

   **Option A — a code editor with built-in notebook support** (VS Code, PyCharm,
   JupyterLab Desktop, and similar all work the same way):
   1. Open the folder these files are in, in the editor.
   2. Open `01_verifier_as_gate.ipynb`.
   3. When prompted for a kernel, choose a Python 3.9+ interpreter.
   4. Run the cells in order, from the top — do not skip ahead.

   **Option B — classic Jupyter in a browser**, if you don't already have an editor
   with notebook support:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # on Windows: .venv\Scripts\activate
   pip install jupyter nbformat
   jupyter notebook 01_verifier_as_gate.ipynb
   ```
   This opens the notebook in your browser. Run the cells in order, from the top.

**No API key. No spending. No network.** Model outputs are recordings; everything
above runs fully offline.

An optional live path (`live_generator.py`) uses the Anthropic API for readers who
want to watch a real model react to verifier feedback. It is strictly optional and
every exercise completes without it.

## Contents

**Numbered files are in the order you would actually open them.** `README.md` has no
number because that convention (start with the file literally named `README`) is
already universal, including on GitHub, which stops rendering it as the folder's
landing page if it is renamed. The `.py` files are not numbered either, for a
different reason: they are Python modules the notebook and `check_materials.py`
`import` by name, and Python cannot import a module whose filename starts with a
digit — numbering them would force a much clumsier import mechanism for no real
benefit, since nobody opens them in reading order anyway.

| # | File | What it is |
|---|---|---|
| | `README.md` | This file. Start here. |
| 1 | `01_verifier_as_gate.ipynb` | The lesson. Four exercises, built in order. |
| 2 | `02_FACILITATOR_GUIDE.md` | For instructors: per-section timing, where learners tend to stall. Read before running a session. |
| 3 | `03_rubric_exercise_4.md` | For instructors: grading rubric for the open-ended Exercise 4. Used after the learner finishes it. |
| 4 | `04_LICENSE-CODE` | MIT license, applies to the `.py` files. |
| 5 | `05_LICENSE-CONTENT` | CC BY 4.0 license, applies to the notebook, docs, and report text. |

Supporting Python modules — imported by the notebook and `check_materials.py`, not
meant to be opened in any particular order:

| File | What it is |
|---|---|
| `redaction_task.py` | Four incident reports with ground truth attached |
| `recorded_generator.py` | Recorded model outputs, with the curation disclosed |
| `verifier_reference.py` | Reference verifiers, plus `KNOWN_GAPS` |
| `solutions/` | Worked solutions to exercises 1–3 |
| `check_materials.py` | Asserts every claim the notebook makes |
| `build_notebook.py` | Regenerates the notebook |
| `live_generator.py` | Optional live-API generator |

The notebook is generated from `build_notebook.py` rather than hand-edited, so the
prose stays reviewable in git.

## The arc

1. A task with two constraints: redact identifiers, preserve operational facts.
2. Why asking a second model to check is circular, costly, and inexact — here.
3. Write the predicate. Return a **reason**, not a boolean.
4. Close the loop. Watch it converge, and cap the iterations.
5. Find the output that passes and should not (`T.L.` for Tomas Lindqvist).
6. Extend the verifier. It now catches that one.
7. Find the one it *still* passes — a definite description that names nobody and
   identifies exactly one person. String matching cannot reach it, because whether
   the phrase identifies someone depends on facts that are not in the text.
8. Decide: extend again, or document the limitation? Defend it.

Step 7 is the point. A verifier supports the claim *no output contains a leak of a
form I check for* — not *no output leaks*. The gap between those is exactly the set
of formats you did not think of, and it is not measurable from inside the system.

## Honest notes

- **The recordings are curated, not sampled.** They were chosen so the verifier has
  something instructive to catch and something instructive to miss. Nothing here is
  a benchmark result, and the notebook says so where a reader might forget.
- **A recording cannot read your feedback.** The loop's *shape* is faithful; its
  responsiveness is simulated. The live path is where that becomes real.
- **The traps were planted by us.** Four reports written by one author cannot stand
  in for the format diversity of a real corpus — which is itself the lesson.
- **Everything is synthetic.** The four incident reports, the names, and the crew
  facts in `redaction_task.py` are invented for this lesson. No real person, real
  incident, or real PII is represented.
- **`verifier_reference.py` is illustrative, not production-grade.** It exists to
  teach the pattern and to give learners something to compare their own `verify_v2`
  against — not to redact real incident reports. A deployed redaction gate would need
  substantially more coverage than a handful of ordinary-language checks, and `KNOWN_GAPS`
  documents specific ways this one falls short of that bar on purpose.

## Level

**Advanced undergraduate.** Assumed: Python (functions, strings, lists) and knowing
what an LLM API call is. Not assumed: reinforcement learning, formal verification, or
statistics.

## License

Created for the NeurIPS 2026 Education Track. Code (`.py` files) is MIT-licensed
(`04_LICENSE-CODE`); the notebook, README, rubric, facilitator guide, and the incident
report text are CC BY 4.0 (`05_LICENSE-CONTENT`). Reuse and adaptation by educators is
explicitly welcome under those terms — attribution is all that is asked.
