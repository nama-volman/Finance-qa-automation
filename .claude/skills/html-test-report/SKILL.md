---
name: html-test-report
description: Run the Finance QA test suite and build the one-page HTML test report (reports/test-report.html). Use when asked for a test report, test results summary, or to present the project's test results.
---

# HTML Test Report

Builds a visual, presentation-ready report of the latest pytest run.

## Steps

1. Run the suite from the project root (takes several minutes, run it in the background):
   `python -m pytest`
   `pytest.ini` already passes `--junitxml=reports/results.xml`, so the results file is written on every run.
2. Build the report:
   `python reports/generate_report.py`
   Output: `reports/test-report.html` (self-contained, open it in any browser).
3. Tell the user the totals (passed / known bugs / failed) and link the report.

## What the report shows

- Verdict with a donut chart and KPI tiles (total, passed, known bugs, failed, run time, pages covered)
- Test flow: every test file in user-journey order (Access → Overview → Money movement → Payment methods → Account & exit), each with its result bar
- The Send Money API flow step by step (token → lookup → quote → execute → balances → history → notification)
- Charts: tests by type (smoke / navigation / functional UI / API / known bug), positive vs negative split, and run time per area
- Bugs found in the app (strict `xfail` tests) and any real failures with their error message
- Collapsible full list of all tests

## Maintaining it

- New test file: add it to `JOURNEY` in `reports/generate_report.py` with a title and a one-line "what it proves". Files not listed there are left out of the flow section.
- Every test carries 2 markers (see `pytest.ini`): `positive` or `negative` first, then one area marker. The positive/negative split is read from the first.
- Test type comes from markers: `xfail` → Known bug, `*_api` module → API, `smoke`, `navigation`, otherwise Functional UI.
- `--fragment` writes the page without `<html>/<head>/<body>` for embedding.
