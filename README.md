# helplessness

A lightweight experiment testing whether prior exposure to inconsistent
(non-contingent) feedback degrades an LLM agent's later performance on a
solvable task — an LLM analog of the classic learned-helplessness paradigm
(Seligman & Maier, 1967).

## Design

1. **30 arithmetic word problems** are generated deterministically
   (`problems.py`), each with a known integer answer, split into:
   - **10 conditioning problems**
   - **20 test problems**

2. **A simulated prior solver's attempts** at the 10 conditioning problems
   are generated (`conditioning.py`), with ~70% correct and ~30% wrong. These
   attempts — and their *true* correctness — are identical across both
   conditions. Only the feedback attached to each attempt differs:
   - **Accurate-feedback condition:** feedback truthfully reports whether
     each attempt was correct.
   - **Random-feedback condition:** the same set of feedback labels, but
     shuffled, so feedback is uncorrelated with actual correctness (a yoked
     control, in learned-helplessness terms).

   Both transcripts are rendered as alternating `user` (problem) /
   `assistant` (attempt) / `user` (feedback) messages — few-shot conditioning
   via prior conversation turns, not live model output.

3. **Both conditioning transcripts are then used as a prefix** for 20
   independent test calls each (one per test problem), with **no feedback
   given during the test phase**. The model just solves each problem cold,
   with the conditioning history as context. This isolates the effect of the
   *feedback contingency* the model was previously exposed to.

4. Each response is parsed (`scoring.py`) for:
   - **Correctness** — a parsed `Answer: <number>` matching the true answer.
   - **Give-up / refusal** — give-up language (e.g. "I don't know", "I
     can't solve this") or the absence of any parseable answer at all.

5. Results are aggregated (`analysis.py`) into a comparison table across the
   two conditions: N, accuracy, and give-up rate.

## Files

| File | Responsibility |
|---|---|
| `config.py` | Model, sample sizes, seeds, system prompt — tweak the experiment here |
| `problems.py` | Generates the 30 word problems |
| `conditioning.py` | Builds simulated attempts and the two feedback conditions |
| `scoring.py` | Extracts answers and detects give-up language from response text |
| `analysis.py` | Aggregates results into a comparison table |
| `run_experiment.py` | Orchestrates the run, calls the API, logs results |

Each piece is independent — swap in a different problem generator, a
different give-up heuristic, or a different model in `config.py` without
touching the rest.

## Running it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # or `set` on Windows cmd, $env: on PowerShell
python run_experiment.py
```

This makes 40 API calls (20 test problems × 2 conditions) to
`claude-sonnet-5` and writes:

- `results/raw_<timestamp>.json` — every response, parsed and unparsed
- `results/comparison_<timestamp>.md` — the summary table

To sanity-check the prompt construction without spending API credits or
needing a key:

```bash
python run_experiment.py --dry-run
```

## Interpreting results

This is a small, single-run experiment (n=20 per condition) meant as a quick
signal, not a publishable finding. A lower accuracy or higher give-up rate in
the `random_feedback` condition vs. `accurate_feedback` would be consistent
with a helplessness-like effect. Re-run with different seeds
(`config.PROBLEM_SEED`, `config.ATTEMPT_SEED`, `config.SHUFFLE_SEED`) or a
larger `N_TEST` to check robustness before drawing conclusions.
