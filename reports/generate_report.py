"""
Build a one-page HTML test report from the JUnit XML that pytest writes.

Usage (from the project root):
    pytest                                   # pytest.ini writes reports/results.xml
    python reports/generate_report.py        # -> reports/test-report.html

Optional arguments:
    python reports/generate_report.py <results.xml> <output.html>
"""

import ast
import html
import platform
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XML = ROOT / "reports" / "results.xml"
DEFAULT_OUT = ROOT / "reports" / "test-report.html"
SITE = "dummypay.vercel.app"

# ---------------------------------------------------------------------------
# The user journey: every test module in the order a real user meets the app.
# phase -> list of (module, title, what the module proves)
# ---------------------------------------------------------------------------
JOURNEY = [
    ("Access", [
        ("test_login_page", "Sign in",
         "Login form loads, both users can sign in, and every invalid input shows the right error."),
        ("test_forgot_password_page", "Password recovery",
         "Reset form accepts a valid email and rejects empty or malformed ones."),
    ]),
    ("Overview", [
        ("test_navigation", "Sidebar & account menu",
         "Each of the 8 sidebar links opens its page; the account menu opens Profile & Settings."),
        ("test_dashboard_page", "Dashboard",
         "Total balance equals the sum of all wallets; wallet count and preferred currency match."),
        ("test_notifications_page", "Notifications",
         "Page loads and switches between All and Unread."),
    ]),
    ("Money movement", [
        ("test_wallets_page", "Wallets & conversion",
         "Currency calculator converts both ways for every currency and rejects bad amounts."),
        ("test_send_money_page", "Send money (UI)",
         "Recipient step opens, Continue moves to the amount step and Back returns."),
        ("test_send_money_api", "Send money (API)",
         "A real transfer through the backend: balances, history and notification all update."),
        ("test_transaction_history_page", "Transaction history",
         "Date, currency and type filters narrow the list; details open on click."),
    ]),
    ("Payment methods", [
        ("test_payment_cards_page", "Payment cards",
         "Add a valid card, reject invalid number or expiry, delete a card, detect duplicates."),
        ("test_bank_accounts_page", "Bank accounts",
         "Add an account, reject 3- and 21-digit numbers, delete the account."),
    ]),
    ("Account & exit", [
        ("test_profile_settings_page", "Profile & settings",
         "Display name 2-50 chars is enforced; preferred currency can be changed."),
        ("test_sign_out", "Sign out",
         "Sign out from any page, protected pages are blocked after, and sign in works again."),
    ]),
]

API_STEPS = [
    ("Get tokens", "Both users sign in through Supabase Auth"),
    ("Lookup", "Sender finds the receiver by email"),
    ("Quote", "create_transfer_quote locks rate for 60s"),
    ("Execute", "execute_transfer with an idempotency key"),
    ("Balances", "Sender -amount, receiver +converted amount"),
    ("History", "Transfer appears in receiver's list"),
    ("Notify", "One payment_received notification"),
]

# The area markers from pytest.ini (every test has positive/negative + exactly one of these)
AREAS = ["smoke", "navigation", "login", "dashboard", "wallets", "historyFilters",
         "cards", "bankAccounts", "profile", "api"]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def read_markers() -> dict:
    """module -> {test function name -> set of pytest.mark names} (read from the source)."""
    result = {}
    for path in (ROOT / "tests").glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        funcs = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names = set()
                for dec in node.decorator_list:
                    target = dec.func if isinstance(dec, ast.Call) else dec
                    if isinstance(target, ast.Attribute):
                        names.add(target.attr)
                funcs[node.name] = names
        result[path.stem] = funcs
    return result


def pretty_name(raw: str) -> tuple[str, str]:
    """'test_convert_to_preferred_currency[chromium-EUR]' -> ('Convert to preferred currency', 'EUR')."""
    base, _, params = raw.partition("[")
    params = params.rstrip("]").replace("chromium-", "").replace("chromium", "")
    text = base.removeprefix("test_").replace("_", " ")
    return text[:1].upper() + text[1:], params


def load_results(xml_path: Path) -> dict:
    tree = ET.parse(xml_path)
    suite = tree.getroot()
    if suite.tag == "testsuites":
        suite = suite[0]
    markers = read_markers()
    tests = []
    for case in suite.iter("testcase"):
        module = case.get("classname", "").split(".")[-1]
        func = case.get("name", "").split("[")[0]
        marks = markers.get(module, {}).get(func, set())

        status, message = "passed", ""
        for child in case:
            if child.tag in ("failure", "error"):
                status, message = "failed", child.get("message", "")
            elif child.tag == "skipped":
                if child.get("type") == "pytest.xfail":
                    status, message = "xfail", child.get("message", "")
                else:
                    status, message = "skipped", child.get("message", "")

        area = next((a for a in AREAS if a in marks), "unmarked")
        title, params = pretty_name(case.get("name", ""))
        tests.append({
            "module": module, "title": title, "params": params, "status": status,
            "message": message, "time": float(case.get("time", 0)), "area": area,
            "kind": "negative" if "negative" in marks else "positive",
        })
    stamp = suite.get("timestamp", "")
    return {
        "tests": tests,
        "duration": float(suite.get("time", 0)),
        "timestamp": datetime.fromisoformat(stamp) if stamp else datetime.now(),
    }


def version(pkg: str) -> str:
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return "?"


# ---------------------------------------------------------------------------
# SVG helpers (all colours come from CSS tokens so both themes work)
# ---------------------------------------------------------------------------
def donut(counts: Counter, total: int) -> str:
    r, c = 52, 2 * 3.14159265 * 52
    parts, offset = [], 0.0
    for key in ("passed", "xfail", "failed", "skipped"):
        n = counts.get(key, 0)
        if not n:
            continue
        length = c * n / total
        parts.append(
            f'<circle r="{r}" cx="70" cy="70" class="seg s-{key}" '
            f'stroke-dasharray="{length:.2f} {c - length:.2f}" stroke-dashoffset="{-offset:.2f}"/>'
        )
        offset += length
    rate = 100 * (counts.get("passed", 0) + counts.get("xfail", 0)) / total if total else 0
    return (
        '<svg viewBox="0 0 140 140" class="donut" role="img" '
        f'aria-label="{rate:.0f}% of tests behaved as expected">'
        f'<circle r="{r}" cx="70" cy="70" class="seg track"/>'
        f'<g transform="rotate(-90 70 70)">{"".join(parts)}</g>'
        f'<text x="70" y="68" class="donut-num">{rate:.0f}%</text>'
        '<text x="70" y="88" class="donut-cap">as expected</text></svg>'
    )


def marker_bars(tests: list) -> str:
    """One bar per area marker, split into positive and negative tests."""
    by_area = defaultdict(Counter)
    for t in tests:
        by_area[t["area"]][t["kind"]] += 1
    areas = [a for a in AREAS + ["unmarked"] if a in by_area]
    max_n = max((sum(v.values()) for v in by_area.values()), default=1)
    label_w, bar_w, row_h = 120, 300, 26
    rows = []
    for i, area in enumerate(areas):
        y = i * row_h
        x = label_w
        for kind in ("positive", "negative"):
            n = by_area[area][kind]
            if not n:
                continue
            w = bar_w * n / max_n
            rows.append(f'<rect x="{x:.1f}" y="{y + 5}" width="{w:.1f}" height="15" rx="3" class="b-{kind}"/>')
            x += w
        pos, neg = by_area[area]["positive"], by_area[area]["negative"]
        rows.append(f'<text x="{label_w - 10}" y="{y + 17}" class="axis mono" text-anchor="end">{area}</text>')
        rows.append(f'<text x="{x + 8:.1f}" y="{y + 17}" class="val">{pos} + {neg}</text>')
    h = row_h * len(areas)
    return (f'<svg viewBox="0 0 {label_w + bar_w + 60} {h}" class="hbars" role="img" '
            f'aria-label="Tests per area marker, positive and negative">{"".join(rows)}</svg>')


def kind_split(tests: list) -> str:
    """One 100% bar: positive vs negative tests (from the first pytest marker)."""
    c = Counter(t["kind"] for t in tests)
    pos, neg = c["positive"], c["negative"]
    total = pos + neg or 1
    return (
        '<div class="split"><h3>Positive vs negative</h3>'
        f'<div class="splitbar"><span class="sp-pos" style="flex:{pos}">{pos}</span>'
        f'<span class="sp-neg" style="flex:{neg}">{neg}</span></div>'
        f'<div class="splitlbl"><span><b>positive</b> · valid input, the feature works · {100 * pos / total:.0f}%</span>'
        f'<span><b>negative</b> · invalid input, blocked action or enforced rule · {100 * neg / total:.0f}%</span></div></div>'
    )


def duration_bars(module_stats: list) -> str:
    max_t = max((m["time"] for m in module_stats), default=1) or 1
    label_w, bar_w, row_h = 160, 260, 24
    rows = []
    for i, m in enumerate(sorted(module_stats, key=lambda m: -m["time"])):
        y = i * row_h
        w = max(bar_w * m["time"] / max_t, 2)
        rows.append(f'<text x="{label_w - 10}" y="{y + 16}" class="axis" text-anchor="end">{html.escape(m["title"])}</text>')
        rows.append(f'<rect x="{label_w}" y="{y + 5}" width="{w:.1f}" height="13" rx="3" class="b-time"/>')
        rows.append(f'<text x="{label_w + w + 8:.1f}" y="{y + 16}" class="val">{m["time"]:.0f}s</text>')
    h = row_h * len(module_stats)
    return (f'<svg viewBox="0 0 {label_w + bar_w + 50} {h}" class="hbars" role="img" '
            f'aria-label="Run time per area">{"".join(rows)}</svg>')


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
STATUS_LABEL = {"passed": "Passed", "failed": "Failed", "xfail": "Known bug", "skipped": "Skipped"}


def build_html(data: dict, standalone: bool = True) -> str:
    tests = data["tests"]
    total = len(tests)
    counts = Counter(t["status"] for t in tests)
    by_module = defaultdict(list)
    for t in tests:
        by_module[t["module"]].append(t)

    # ---- journey ----
    module_stats, phases_html = [], []
    for phase, modules in JOURNEY:
        cards = []
        for module, title, proves in modules:
            mts = by_module.get(module, [])
            if not mts:
                continue
            c = Counter(t["status"] for t in mts)
            mtime = sum(t["time"] for t in mts)
            module_stats.append({"title": title, "time": mtime})
            state = "failed" if c["failed"] else ("xfail" if c["xfail"] else "passed")
            seg = "".join(
                f'<span class="seg-{s}" style="flex:{c[s]}"></span>'
                for s in ("passed", "xfail", "failed", "skipped") if c[s]
            )
            note = f'<span class="chip chip-xfail">{c["xfail"]} known bug</span>' if c["xfail"] else ""
            if c["failed"]:
                note += f'<span class="chip chip-failed">{c["failed"]} failed</span>'
            if c["skipped"]:
                note += f'<span class="chip chip-skipped">{c["skipped"]} skipped</span>'
            kinds = Counter(t["kind"] for t in mts)
            areas = " ".join(f'<span class="mk">@{a}</span>' for a in AREAS if any(t["area"] == a for t in mts))
            cards.append(f"""
          <article class="stage st-{state}">
            <header><h4>{title}</h4><span class="count">{c['passed'] + c['xfail']}/{len(mts)}</span></header>
            <p>{proves}</p>
            <div class="marks">{areas}<span class="pn"><b class="pn-pos">{kinds['positive']} positive</b> · <b class="pn-neg">{kinds['negative']} negative</b></span></div>
            <div class="minibar">{seg}</div>
            <footer><code>{module}.py</code><span>{mtime:.0f}s</span>{note}</footer>
          </article>""")
        phases_html.append(f"""
      <li class="phase">
        <div class="phase-label"><span class="dot"></span>{phase}</div>
        <div class="stages">{''.join(cards)}</div>
      </li>""")

    # ---- known bugs ----
    bugs = [t for t in tests if t["status"] == "xfail"]
    bugs_html = "".join(
        f'<li><strong>{html.escape(b["title"])}</strong><span>{html.escape(b["message"].removeprefix("reason: "))}</span></li>'
        for b in bugs
    ) or "<li><span>No known bugs recorded in this run.</span></li>"

    # ---- skipped (data-dependent preconditions) ----
    skipped = [t for t in tests if t["status"] == "skipped"]
    skipped_html = ""
    if skipped:
        items = "".join(
            f'<li><strong>{html.escape(t["title"])}{f" ({html.escape(t["params"])})" if t["params"] else ""}</strong>'
            f'<span>{html.escape(t["message"])}</span></li>' for t in skipped)
        skipped_html = (
            '<div class="skipbox"><h3>Skipped on purpose</h3>'
            '<p class="sub">These tests check their precondition against the live account first and skip '
            'when it does not apply, instead of failing for the wrong reason.</p>'
            f'<ul class="skiplist">{items}</ul></div>')

    # ---- failures ----
    failed = [t for t in tests if t["status"] == "failed"]
    failed_html = ""
    if failed:
        items = "".join(
            f'<li><strong>{html.escape(t["title"])}</strong> <code>{t["module"]}</code>'
            f'<pre>{html.escape(t["message"][:400])}</pre></li>' for t in failed)
        failed_html = f'<section class="block fail-block"><h2>Failures to look at</h2><ul class="fails">{items}</ul></section>'

    # ---- API flow ----
    api_tests = by_module.get("test_send_money_api", [])
    api_ok = api_tests and all(t["status"] == "passed" for t in api_tests)
    api_html = "".join(
        f'<li><span class="n">{i}</span><b>{name}</b><small>{desc}</small></li>'
        for i, (name, desc) in enumerate(API_STEPS, 1)
    )

    # ---- full list ----
    detail_rows = []
    for _, modules in JOURNEY:
        for module, title, _ in modules:
            rows = "".join(
                f'<tr><td>{html.escape(t["title"])}'
                f'{f" <em>{html.escape(t["params"])}</em>" if t["params"] else ""}</td>'
                f'<td><span class="mk mk-{t["kind"]}">@{t["kind"]}</span> <span class="mk">@{t["area"]}</span></td>'
                f'<td class="num">{t["time"]:.1f}s</td>'
                f'<td><span class="pill p-{t["status"]}">{STATUS_LABEL[t["status"]]}</span></td></tr>'
                for t in by_module.get(module, []))
            if rows:
                detail_rows.append(f'<tr class="grp"><th colspan="4">{title}</th></tr>{rows}')

    run_at = data["timestamp"].strftime("%d %b %Y, %H:%M")
    mins, secs = divmod(int(data["duration"]), 60)
    expected = counts["passed"] + counts["xfail"]
    verdict = ("All tests behaved as expected" if not counts["failed"]
               else f'{counts["failed"]} test{"s" if counts["failed"] > 1 else ""} need attention')
    kind_counts = Counter(t["kind"] for t in tests)

    body = f"""<title>DummyPay QA Report</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header class="hero">
    <div class="eyebrow">Final QA project · Automated test report</div>
    <h1>Finance QA Automation</h1>
    <p class="lede">End-to-end UI and API tests for the <b>DummyPay</b> finance web app, written in Python with
      Playwright and pytest using the Page Object Model.</p>
    <dl class="meta">
      <div><dt>Run</dt><dd>{run_at}</dd></div>
      <div><dt>Target</dt><dd>{SITE}</dd></div>
      <div><dt>Browser</dt><dd>Chromium</dd></div>
      <div><dt>Stack</dt><dd>Python {platform.python_version()} · Playwright {version("playwright")} · pytest {version("pytest")}</dd></div>
    </dl>
  </header>

  <section class="summary">
    <div class="verdict v-{'ok' if not counts['failed'] else 'bad'}">
      {donut(counts, total)}
      <div>
        <h2>{verdict}</h2>
        <p>{expected} of {total} tests gave the expected result. {counts['xfail']} of them are
          strict <code>xfail</code> tests that document real bugs in the app.{
          f" {counts['skipped']} skipped because their precondition did not apply to the account." if counts["skipped"] else ""}</p>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><span class="k-num">{total}</span><span class="k-lbl">Tests run</span></div>
      <div class="kpi k-pass"><span class="k-num">{counts['passed']}</span><span class="k-lbl">Passed</span></div>
      <div class="kpi k-xfail"><span class="k-num">{counts['xfail']}</span><span class="k-lbl">Known bugs</span></div>
      <div class="kpi k-fail"><span class="k-num">{counts['failed']}</span><span class="k-lbl">Failed</span></div>
      <div class="kpi"><span class="k-num">{mins}:{secs:02d}</span><span class="k-lbl">Run time (min)</span></div>
      <div class="kpi"><span class="k-num">{kind_counts['positive']}<small> / </small>{kind_counts['negative']}</span><span class="k-lbl">Positive / negative</span></div>
    </div>
  </section>

  <section class="block">
    <h2>Test flow</h2>
    <p class="sub">The suite follows the path a real user takes through the app, from signing in to signing out.
      Each card is one test file; the bar shows its results.</p>
    <ol class="journey">{''.join(phases_html)}
    </ol>
  </section>

  <section class="block api">
    <div class="api-head">
      <h2>Money transfer, verified through the API</h2>
      <span class="pill p-{'passed' if api_ok else 'failed'}">{'All API checks passed' if api_ok else 'API checks need attention'}</span>
    </div>
    <p class="sub">The UI tests check what the user sees. This flow checks that the money really moves:
      two real accounts, one transfer, and every side effect confirmed in the backend.
      Negative cases cover sending to yourself, an unknown or malformed email, and insufficient funds.</p>
    <ol class="steps">{api_html}</ol>
  </section>

  <section class="grid2">
    <div class="block">
      <h2>Tests by marker</h2>
      <p class="sub">Every test carries two pytest markers: <code>positive</code> or <code>negative</code> first,
        then the area it belongs to. Any group runs on its own, e.g. <code>pytest -m "negative and cards"</code>.</p>
      {marker_bars(tests)}
      <div class="legend"><span class="l-positive">positive</span><span class="l-negative">negative</span></div>
      {kind_split(tests)}
    </div>
    <div class="block">
      <h2>Run time by area</h2>
      {duration_bars(module_stats)}
    </div>
  </section>

  <section class="block bugs">
    <h2>Bugs found in the app</h2>
    <p class="sub">Marked <code>xfail(strict=True)</code>: the test passes the build while the bug exists, and turns red
      the day it is fixed, so the marker can be removed.</p>
    <ul class="buglist">{bugs_html}</ul>
    {skipped_html}
  </section>
  {failed_html}

  <section class="block">
    <details>
      <summary>All {total} tests</summary>
      <div class="tablewrap"><table>
        <thead><tr><th>Test</th><th>Markers</th><th class="num">Time</th><th>Result</th></tr></thead>
        <tbody>{''.join(detail_rows)}</tbody>
      </table></div>
    </details>
  </section>

  <footer class="foot">
    <span>How it is built: tests → page objects (<code>pages/</code>) → Playwright → DummyPay UI ·
      API tests → <code>api/</code> → Supabase REST &amp; RPC</span>
    <span>Generated by <code>reports/generate_report.py</code></span>
  </footer>
</div>"""
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                f'</head>\n<body>\n{body}\n</body>\n</html>\n')
    return body


CSS = """
/* Layout: one centred column; a vertical journey rail with phase groups, charts side by side below. */
:root{
  --bg:#f3f5f7; --surface:#ffffff; --ink:#14202b; --muted:#5b6875; --line:#dde3e9;
  --accent:#0b5f73; --accent-soft:#e2eff2;
  --pass:#1f8a5b; --pass-soft:#e3f3ea; --xfail:#b7791f; --xfail-soft:#fbf0dc;
  --fail:#c2413a; --fail-soft:#fbe5e3; --time:#4f7d8c; --neg:#6a4fb3; --neg-soft:#ece7f7;
  --f-display:"Manrope",system-ui,sans-serif; --f-body:"IBM Plex Sans",system-ui,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0e161d; --surface:#15212a; --ink:#e4ebf0; --muted:#93a3b0; --line:#253541;
  --accent:#5cc3d6; --accent-soft:#16303a;
  --pass:#4cc38a; --pass-soft:#143428; --xfail:#e3a948; --xfail-soft:#3a2d15;
  --fail:#f0736b; --fail-soft:#3d1c1a; --time:#6fa3b3; --neg:#a993ee; --neg-soft:#2a2342; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0e161d; --surface:#15212a; --ink:#e4ebf0; --muted:#93a3b0; --line:#253541;
  --accent:#5cc3d6; --accent-soft:#16303a;
  --pass:#4cc38a; --pass-soft:#143428; --xfail:#e3a948; --xfail-soft:#3a2d15;
  --fail:#f0736b; --fail-soft:#3d1c1a; --time:#6fa3b3; --neg:#a993ee; --neg-soft:#2a2342; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--f-body)}
code{font-family:var(--f-mono);font-size:.86em;background:var(--accent-soft);color:var(--accent);padding:.05em .35em;border-radius:4px}
.wrap{max-width:1080px;margin:0 auto;padding-block:40px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:22px}
h1,h2,h4{font-family:var(--f-display);text-wrap:balance;margin:0}
h1{font-size:clamp(2rem,4.5vw,2.9rem);font-weight:800;letter-spacing:-.02em}
h2{font-size:1.22rem;font-weight:700}
.eyebrow{font:500 .74rem var(--f-mono);text-transform:uppercase;letter-spacing:.12em;color:var(--accent)}
.hero{display:flex;flex-direction:column;gap:12px}
.lede{margin:0;max-width:62ch;color:var(--muted);font-size:1.05rem}
.lede b{color:var(--ink)}
.meta{display:flex;flex-wrap:wrap;gap:8px 28px;margin:6px 0 0}
.meta div{display:flex;flex-direction:column}
.meta dt{font:500 .7rem var(--f-mono);text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.meta dd{margin:0;font-weight:500}
.block{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:22px 24px;min-width:0}
.sub{color:var(--muted);margin:6px 0 18px;max-width:75ch}
/* summary */
.summary{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:22px}
.verdict{display:flex;align-items:center;gap:22px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:20px 24px;border-left:5px solid var(--pass)}
.verdict.v-bad{border-left-color:var(--fail)}
.verdict p{margin:6px 0 0;color:var(--muted)}
.donut{width:132px;flex:none}
.seg{fill:none;stroke-width:16}
.track{stroke:var(--line)} .s-passed{stroke:var(--pass)} .s-xfail{stroke:var(--xfail)} .s-failed{stroke:var(--fail)} .s-skipped{stroke:var(--muted)}
.donut-num{font:800 28px var(--f-display);fill:var(--ink);text-anchor:middle}
.donut-cap{font:500 10px var(--f-mono);fill:var(--muted);text-anchor:middle;text-transform:uppercase;letter-spacing:.08em}
.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:flex;flex-direction:column}
.k-num{font:800 1.7rem var(--f-display);font-variant-numeric:tabular-nums}
.k-lbl{font-size:.8rem;color:var(--muted)}
.k-pass .k-num{color:var(--pass)} .k-xfail .k-num{color:var(--xfail)} .k-fail .k-num{color:var(--fail)}
/* journey */
.journey{list-style:none;margin:0;padding:0;position:relative}
.journey::before{content:"";position:absolute;left:7px;top:8px;bottom:8px;width:2px;background:var(--line)}
.phase{position:relative;padding-left:30px;padding-bottom:20px}
.phase:last-child{padding-bottom:0}
.phase-label{font:600 .78rem var(--f-mono);text-transform:uppercase;letter-spacing:.1em;color:var(--accent);margin-bottom:10px;display:flex;align-items:center}
.dot{position:absolute;left:0;width:16px;height:16px;border-radius:50%;background:var(--surface);border:3px solid var(--accent)}
.stages{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.stage{border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:8px;background:var(--bg)}
.stage header{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.stage h4{font-size:1rem}
.stage p{margin:0;font-size:.86rem;color:var(--muted);flex:1}
.count{font:600 .85rem var(--f-mono);color:var(--pass);font-variant-numeric:tabular-nums}
.st-failed .count{color:var(--fail)}
.minibar{display:flex;height:6px;border-radius:3px;overflow:hidden;gap:2px}
.seg-passed{background:var(--pass)} .seg-xfail{background:var(--xfail)} .seg-failed{background:var(--fail)} .seg-skipped{background:var(--muted)}
.stage footer{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:.76rem;color:var(--muted)}
.stage footer code{font-size:.72rem;overflow-wrap:anywhere;min-width:0}
.chip{font:600 .68rem var(--f-mono);padding:1px 7px;border-radius:99px}
.chip-xfail{background:var(--xfail-soft);color:var(--xfail)} .chip-failed{background:var(--fail-soft);color:var(--fail)}
/* api */
.api-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;align-items:center}
.steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;counter-reset:s}
.steps li{position:relative;background:var(--accent-soft);border-radius:8px;padding:12px 10px;display:flex;flex-direction:column;gap:4px}
.steps li:not(:last-child)::after{content:"";position:absolute;right:-7px;top:50%;width:6px;height:6px;border-top:2px solid var(--accent);border-right:2px solid var(--accent);transform:translateY(-50%) rotate(45deg)}
.steps .n{font:600 .7rem var(--f-mono);color:var(--accent)}
.steps b{font-family:var(--f-display);font-size:.92rem}
.steps small{font-size:.74rem;color:var(--muted);line-height:1.35}
/* charts */
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}
.grid2 .block h2{margin-bottom:14px}
.hbars{width:100%;height:auto;display:block}
.axis{font:500 12px var(--f-body);fill:var(--muted)}
.val{font:600 11px var(--f-mono);fill:var(--ink)}
.b-passed{fill:var(--pass)} .b-xfail{fill:var(--xfail)} .b-failed{fill:var(--fail)} .b-skipped{fill:var(--muted)} .b-time{fill:var(--time)}
.legend{display:flex;gap:16px;margin-top:12px;font-size:.8rem;color:var(--muted)}
.legend span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.l-passed::before{background:var(--pass)} .l-xfail::before{background:var(--xfail)} .l-failed::before{background:var(--fail)}
/* bugs & failures */
.buglist,.fails{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.buglist li{display:flex;flex-direction:column;gap:2px;padding:12px 14px;border-radius:8px;background:var(--xfail-soft);border-left:4px solid var(--xfail)}
.buglist span{color:var(--muted);font-size:.88rem}
.l-skipped::before{background:var(--muted)}
.b-positive{fill:var(--accent)} .b-negative{fill:var(--neg)}
.l-positive::before{background:var(--accent)} .l-negative::before{background:var(--neg)}
.axis.mono{font:500 11.5px var(--f-mono)}
.marks{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center}
.mk{font:500 .7rem var(--f-mono);padding:1px 6px;border-radius:4px;background:var(--accent-soft);color:var(--accent);white-space:nowrap}
.mk-negative{background:var(--neg-soft);color:var(--neg)}
.pn{font-size:.74rem;color:var(--muted);flex-basis:100%}
.sub code{white-space:nowrap}
.pn b{font-weight:600}
.pn-pos{color:var(--accent)} .pn-neg{color:var(--neg)}
.k-num small{font-size:.6em;color:var(--muted);font-weight:600}
.split{margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}
.split h3{font:700 1rem var(--f-display);margin:0 0 10px}
.splitbar{display:flex;gap:3px;height:26px;border-radius:6px;overflow:hidden;font:600 .8rem var(--f-mono)}
.splitbar span{display:flex;align-items:center;padding:0 10px;min-width:2.5em}
.sp-pos{background:var(--accent);color:var(--surface)}
.sp-neg{background:var(--neg);color:var(--surface)}
.splitlbl{display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 12px;margin-top:6px;font-size:.78rem;color:var(--muted)}
.chip-skipped{background:var(--line);color:var(--muted)}
.skipbox{margin-top:20px}
.skipbox h3{font:700 1rem var(--f-display);margin:0}
.skipbox .sub{margin-bottom:10px}
.skiplist{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.skiplist li{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:.88rem;padding:8px 12px;border-radius:8px;background:var(--bg);border:1px solid var(--line)}
.skiplist span{color:var(--muted)}
.fail-block{border-color:var(--fail)}
.fails li{padding:10px 14px;border-radius:8px;background:var(--fail-soft)}
.fails pre{white-space:pre-wrap;font:12px/1.4 var(--f-mono);margin:6px 0 0;color:var(--ink)}
/* table */
summary{cursor:pointer;font:700 1.05rem var(--f-display)}
summary:focus-visible{outline:2px solid var(--accent);outline-offset:4px;border-radius:4px}
.tablewrap{overflow-x:auto;margin-top:14px}
table{width:100%;border-collapse:collapse;font-size:.86rem}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}
thead th{font:500 .72rem var(--f-mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
tr.grp th{background:var(--accent-soft);color:var(--accent);font-family:var(--f-display)}
td em{font-style:normal;font-family:var(--f-mono);font-size:.78rem;color:var(--muted)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pill{display:inline-block;font:600 .72rem var(--f-mono);padding:2px 9px;border-radius:99px;white-space:nowrap}
.p-passed{background:var(--pass-soft);color:var(--pass)} .p-xfail{background:var(--xfail-soft);color:var(--xfail)}
.p-failed{background:var(--fail-soft);color:var(--fail)} .p-skipped{background:var(--line);color:var(--muted)}
.foot{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;font-size:.8rem;color:var(--muted)}
@media (max-width:860px){
  .summary,.grid2{grid-template-columns:minmax(0,1fr)}
  .steps{grid-template-columns:repeat(2,minmax(0,1fr))}
  .steps li::after{display:none}
}
@media (max-width:480px){
  .verdict{flex-direction:column;align-items:flex-start}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .block{padding:18px 16px}
}
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    xml_path = Path(args[0]) if args else DEFAULT_XML
    out_path = Path(args[1]) if len(args) > 1 else DEFAULT_OUT
    standalone = "--fragment" not in sys.argv   # --fragment: body only, for embedding
    if not xml_path.exists():
        sys.exit(f"No results file at {xml_path}. Run pytest first.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_html(load_results(xml_path), standalone), encoding="utf-8")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
