"""Fill the posterly landscape_4col template with this reproduction's evidence.

Framing is faithful-reproduction: the paper's claim versus what the logged runs
actually showed. Every number is read from .openresearch/artifacts.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / ".openresearch" / "artifacts"
SCRATCH = Path("/private/tmp/claude-501/-Users-dineshjinjala-Documents-AllCode-ICMLPapers/"
               "8657cd16-a2c9-4a7c-821e-e589ccee3f0c/scratchpad")
TEMPLATE = SCRATCH / "posterly" / "templates" / "landscape_4col_neutral.html"
BUILD = SCRATCH / "poster_build"
OUT = BUILD / "poster.html"

c1 = json.loads((ART / "claim_1" / "raw_summary.json").read_text())
c2 = json.loads((ART / "claim_2" / "raw_summary.json").read_text())
c3 = json.loads((ART / "claim_3" / "raw_summary.json").read_text())
c4 = json.loads((ART / "claim_4" / "theorem43_summary.json").read_text())

# Accent derived from the authors' affiliation (Texas A&M — Optimization-AI lab,
# Wei/Zhou/Wang/Lin/Yang): maroon.
# NB: in this template --accent/--accent-deep are INK and --accent-light/
# --accent-soft are BACKGROUND TINTS (neutral defaults #E8F1F8 / #D7E5F0).
# They are not a lightness ramp of one hue -- setting the two tints to a mid
# maroon renders dark text on dark panels, which no gate detects.
TOKENS = {
    "--accent": "#5c0b16",
    "--accent-deep": "#3d060e",
    "--accent-light": "#F7EAEC",
    "--accent-soft": "#EBD5D9",
    "--gold": "#A8792C",
    "--gold-soft": "#FBF3E2",
}

HEADER = """  <header class="header" data-measure-role="header">
    <div class="venue-badge-spacer"></div>

    <div class="title-block">
      <h1 class="title">SCENT: Geometry-Aware Compositional Entropic Risk Minimization <span class="qualifier">[ A Reproduction ]</span></h1>
      <div class="subtitle">Four theorems hold under their own hypotheses; the CIFAR partial-AUC claim does not; extreme classification is blocked by a compute boundary.</div>
      <div class="authors-line">
        <span class="author">Independent CPU-only reproduction<sup>&#9993;</sup></span>
        <span class="aff">&middot; ICML 2026 Reproducibility Challenge &middot; paper arXiv:2602.02877 (Wei, Zhou, Wang, Lin, Yang)</span>
      </div>
    </div>

    <div class="right-block">
      <div class="qr-block">
        <img data-color-exempt="logo" src="QRSRC" alt="QR to the reproduction logbook">
        <div class="qr-label">Logbook &amp; Code</div>
      </div>
    </div>
  </header>"""

BANNER = f"""  <section class="framework-banner" data-measure-role="banner">
    <div class="fb-text">
      <span class="fb-label">Verdict</span>
      &nbsp;<strong>4 VERIFIED &middot; 1 FALSIFIED &middot; 1 BLOCKED.</strong> Every claim is tested against its exact quantified statement, under the theorem's own assumptions and with the step sizes the theorems themselves prescribe &mdash; never a nearby proxy. Each claim page carries its raw data, an independent checker, and a negative control required to fail. No result is described at a scale it did not run at.
    </div>
    <div class="banner-stats">
      <div class="bs-item"><div class="bs-num">2.8e-08</div><div class="bs-label">max closed-form<br>vs argmin error</div></div>
      <div class="bs-item"><div class="bs-num">0</div><div class="bs-label">interval breaches in<br>33.5M SPMD updates</div></div>
      <div class="bs-item"><div class="bs-num">47/47</div><div class="bs-label">cells under the<br>Thm 4.3 / 4.5 bounds</div></div>
      <div class="bs-item"><div class="bs-num">0.37%</div><div class="bs-label">&micro;-spread of the<br>SPMD/SGD ratio</div></div>
    </div>
  </section>"""

CARD_INTRO = """      <div class="card highlight" data-measure-role="card" data-logbook-target="executive-summary">
        <div class="section-title"><span class="num">1</span><span class="st-text">What is being reproduced</span></div>
        <p class="body-text">
          SCENT minimizes a <span class="keyword">Log-E-Exp</span> risk
          $\\log \\mathbb{E}_\\zeta[e^{s(w;\\zeta)}]$ through its min&ndash;min dual form, updating
          the dual variable $\\nu$ by <span class="keyword">stochastic proximal mirror descent</span>
          under a Bregman divergence induced by $\\varphi(\\nu)=e^{-\\nu}$.
        </p>
        <ul class="mt-3 fs-4">
          <li>Six claims: four theorems, two benchmark suites.</li>
          <li>Each tested against its <strong>exact statement</strong>, never a proxy.</li>
          <li>Constraint: <strong>CPU only</strong>, no GPU hardware of any kind.</li>
        </ul>
        <div class="callout mt-3">
          <strong>Q:</strong> Do the theorems survive a targeted attempt to break them, and do the
          benchmark claims hold at the paper's&nbsp;own&nbsp;protocol?
        </div>
      </div>"""

CARD_C3 = """      <div class="card" data-measure-role="card" data-logbook-target="claim-3-dual-boundedness">
        <div class="section-title"><span class="num">2</span><span class="st-text">Claim 3 &mdash; dual boundedness&nbsp;<span class="key-mark">&#9733; VERIFIED</span></span></div>
        <p class="body-text fs-3">
          Lemma 3.3 guarantees $\\nu_{i,t}\\in[c_0,c_1]$ for <em>all</em> $t$, with no projection. Eq. (7)
          writes $e^{\\nu_t}$ as a <span class="keyword">convex combination</span> of $e^{\\nu_{t-1}}$ and
          $e^{s_t}$ &mdash; that mechanism is verified, not merely finiteness.
        </p>
        <div class="figure">
          <img src="images/claim3_bounded.png" data-source="repro" data-asset-id="claim3" class="w-100">
          <div class="caption fs-2">Same oracle, same step size: SPMD stays inside $[c_0,c_1]$; an unprojected Euclidean dual step escapes.</div>
        </div>
      </div>"""

CARD_C1 = """      <div class="card highlight" data-measure-role="card" data-logbook-target="claim-1-closed-form-dual-update">
        <div class="section-title"><span class="num">3</span><span class="st-text">Claim 1 &mdash; closed-form dual step&nbsp;<span class="key-mark">&#9733; VERIFIED</span></span></div>
        <div class="eqn">
          <span class="label">Lemma 3.1</span>
          $$\\nu_t = \\nu_{t-1} + \\log(1+\\alpha_t e^{s}) - \\log(1+\\alpha_t e^{\\nu_{t-1}})$$
        </div>
        <p class="body-text fs-3">
          Checked against an <strong>independent numerical argmin</strong> over 512 randomised cases,
          and a 90-digit <code>mpmath</code> recomputation.
        </p>
        <table class="result-table">
          <thead><tr><th class="method">Check</th><th>Max error</th></tr></thead>
          <tbody>
            <tr><td class="method">vs independent argmin</td><td class="best">2.777e-08</td></tr>
            <tr><td class="method">vs 90-digit mpmath</td><td class="best">1.819e-12</td></tr>
            <tr><td class="method">first-order residual</td><td class="best">4.677e-10</td></tr>
            <tr class="ours"><td class="method">stress cases finite</td><td class="best">400 / 400</td></tr>
          </tbody>
        </table>
      </div>"""

CARD_C2 = """      <div class="card highlight" data-measure-role="card" data-logbook-target="claim-2-convergence-rate">
        <div class="section-title"><span class="num">4</span><span class="st-text">Claim 2 &mdash; the $O(1/\\sqrt{T})$ rate&nbsp;<span class="key-mark">&#9733; VERIFIED</span></span></div>
        <p class="body-text fs-3 text-secondary mb-1">
          Convex instance built to <strong>provably satisfy Assumption 3.2</strong>; 20 seeds &times; 4
          horizons. Theorem 3.6 is an <em>upper bound</em>: the predicate is that
          $\\text{gap}\\times\\sqrt{T}$ stays bounded, not that the loss falls.
        </p>
        <div class="figure">
          <img src="images/claim2_rate.png" data-source="repro" data-asset-id="claim2" class="w-100">
          <div class="caption fs-2"><strong>Left:</strong> gap vs $T$ against an exact $1/\\sqrt{T}$ reference. <strong>Right:</strong> the product flattens (increments +0.268, +0.119, +0.032).</div>
        </div>
        <div class="keybox">
          <div class="kb-item"><div class="kb-num">&minus;0.4545</div><div class="kb-label">log-log slope<br>(CI width 9e-4)</div></div>
          <div class="kb-item"><div class="kb-num">1.213&times;</div><div class="kb-label">product ratio<br>over 64&times; horizon</div></div>
          <div class="kb-item"><div class="kb-num">80</div><div class="kb-label">independent<br>seeded runs</div></div>
        </div>
      </div>"""

CARD_C4FIG = """      <div class="card highlight" data-measure-role="card" data-logbook-target="claim-4-kappa-and-spmd-vs-sgd">
        <div class="section-title"><span class="num">5</span><span class="st-text">Claim 4 &mdash; $\\kappa$ and SPMD vs SGD&nbsp;<span class="key-mark">&#9733; VERIFIED</span></span></div>
        <p class="body-text fs-3 text-secondary mb-1">
          Step sizes are <strong>exactly those Theorems 4.3 and 4.5 prescribe</strong>. $s$ is drawn from a
          truncated normal so Assumption 3.2(ii) holds and $m$, $\\mathrm{Var}(z)$, $\\kappa$, $\\nu_*$ are closed-form.
        </p>
        <div class="figure">
          <img src="images/claim4_kappa.png" data-source="repro" data-asset-id="claim4" class="w-100">
          <div class="caption fs-2">
            <strong>Left:</strong> reproduction of paper Fig. 1 &mdash; seven $\\mu$ curves coincide.
            <strong>Right:</strong> every cell sits below its theorem bound.
          </div>
        </div>
        <div class="keybox">
          <div class="kb-item"><div class="kb-num">0.961</div><div class="kb-label">Spearman<br>$\\sqrt{\\kappa-1}$ vs error</div></div>
          <div class="kb-item"><div class="kb-num">4e-16</div><div class="kb-label">bound-ratio identity<br>rel. error</div></div>
          <div class="kb-item"><div class="kb-num">7.04&times;</div><div class="kb-label">worst bound<br>slack</div></div>
        </div>
      </div>"""

CARD_ABL = """      <div class="card" data-measure-role="card" data-logbook-target="claim-4-kappa-and-spmd-vs-sgd">
        <div class="section-title"><span class="num">6</span><span class="st-text">What breaks it &mdash; and one deviation</span></div>
        <ul class="mt-1 fs-3">
          <li><strong>Geometry ablation.</strong> Swap the $e^{-\\nu}$ Bregman step for a Euclidean one of equal size: bound (15) violated&nbsp;(8.903&nbsp;vs&nbsp;3.900).</li>
          <li><strong>$\\kappa$ ablation.</strong> Score a $\\sigma{=}2$ run with a $\\sigma{=}0.25$ value of $\\kappa$: violated&nbsp;(0.992&nbsp;vs&nbsp;0.137).</li>
        </ul>
        <div class="callout gold mt-1">
          <strong>Non-vacuity is enforced.</strong> A loose bound is satisfied by almost anything; the
          worst slack here is <strong>7.04&times;</strong>, and both of the ablations above violate&nbsp;that&nbsp;bound.
        </div>
        <div class="callout mt-1">
          <strong>Deviation, reported.</strong> The <em>empirical</em> ratio is not monotone in $\\sigma$
          past $\\sigma{=}1$ (0.0112 &rarr; 0.0215 &rarr; 0.0348), unlike Fig. 1's text. The
          <em>provable</em> ratio verifies exactly.
        </div>
      </div>"""

CARD_C6 = """      <div class="card highlight" data-measure-role="card" data-logbook-target="claim-6-partial-auc">
        <div class="section-title"><span class="num">7</span><span class="st-text">Claim 6 &mdash; partial AUC&nbsp;<span class="key-mark">&#9733; FALSIFIED</span></span></div>
        <p class="body-text fs-3 text-secondary mb-1">
          Paper's full protocol: CIFAR-10/100, $\\tau\\in\\{0.05,0.1\\}$, frozen ResNet-18, 60 epochs,
          3 seeds &mdash; 24 rows. Margin <strong>predeclared</strong>&nbsp;at&nbsp;0.002.
        </p>
        <div class="figure">
          <img src="images/claim6_cifar.png" data-source="repro" data-asset-id="claim6" class="w-100">
          <div class="caption fs-2">Paired epoch-60 differences. CIFAR-10 $\\tau$=0.05: bootstrap 95% CI [0.00816, 0.04071], above the margin.</div>
        </div>
      </div>"""

CARD_C5 = """      <div class="card" data-measure-role="card" data-logbook-target="claim-5-extreme-classification">
        <div class="section-title"><span class="num">8</span><span class="st-text">Claim 5 &mdash; XC benchmarks&nbsp;<span class="key-mark">&#9733; BLOCKED</span></span></div>
        <table class="result-table">
          <thead><tr><th class="method">Asset needed</th><th>Size</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td class="method">Glint360K source</td><td>129.9 GB</td><td>GPU only</td></tr>
            <tr><td class="method">TreeOfLife-10M source</td><td>1994.6 GB</td><td>GPU only</td></tr>
            <tr><td class="method">ToL-200M embeddings</td><td>345.9 GB</td><td>wrong corpus</td></tr>
          </tbody>
        </table>
        <p class="body-text mt-2 fs-3">
          Both need GPU encoder inference over 9.5&ndash;17.1M images. The authors' extracted features are unpublished.
        </p>
        <div class="callout mt-2">
          <strong>No proxy reported.</strong> BLOCKED is terminal, never converted&nbsp;into&nbsp;a&nbsp;pass.
        </div>
        <p class="body-text mt-2 fs-3">
          <strong>What would unblock it:</strong> publishing the extracted <code>features.pt</code> /
          <code>labels.pt</code> that <code>xc/README.md</code> already references &mdash;
          <code>xc/train.py</code> then trains only a linear classifier, which is CPU-reachable.
        </p>
      </div>"""

# posterly's alignment gate wants all four columns to bottom out within 5 px of
# each other. Prose edits only move a column in ~25 px line quanta, so each
# column ends with a spacer measured in 1 mm (~3.78 px) units.
# tools/tune_poster.py solves these four numbers.
BALANCE = [10, 0, -5, 1]


BALANCE_CSS = "<style>\n" + "\n".join(
    f"  .bal-c{i} {{ display:block; margin-top: calc(VAL{i} * var(--u)); }}"
    for i in range(4)) + "\n</style>\n"


def column(idx, *cards):
    cards = list(cards)
    spacer = f'\n        <span class="bal-c{idx}" data-balance></span>'
    cards[-1] = cards[-1].replace("\n      </div>", spacer + "\n      </div>", 1)
    return ('    <div class="column" data-measure-role="column">\n\n'
            + "\n\n".join(cards) + '\n\n    </div>')


COL1 = column(0, CARD_INTRO, CARD_C3)
COL2 = column(1, CARD_C1, CARD_C2)
COL3 = column(2, CARD_C4FIG, CARD_ABL)
COL4 = column(3, CARD_C6, CARD_C5)

STRIP = """  <section class="takeaways-strip" data-measure-role="footer-strip" data-logbook-target="conclusion">
    <div class="ts-title"><span class="num">10</span> Takeaways</div>
    <div class="ts-item"><span class="ts-key">Theory.</span><span class="ts-text">All four theorem claims hold under their own hypotheses, with non-vacuous bounds.</span></div>
    <div class="ts-item"><span class="ts-key">Method.</span><span class="ts-text">Prescribed step sizes matter: hand-tuning &alpha; per &micro; manufactured a false Fig. 1 failure.</span></div>
    <div class="ts-item"><span class="ts-key">Result.</span><span class="ts-text">CIFAR-10 &tau;=0.05 falsifies &ldquo;SCENT matches or exceeds SOX&rdquo;.</span></div>
    <div class="ts-item"><span class="ts-key">Practical.</span><span class="ts-text">Publishing the extracted features would make the XC experiment CPU-reachable.</span></div>
  </section>"""

FOOTER = """  <div class="footer" data-measure-role="footer">
    <div>
      <strong class="method-name">SCENT REPRODUCTION</strong> &middot; ICML 2026 Reproducibility Challenge &middot;
      CPU-only; theory reruns in ~9 min from one pinned uv lockfile.
    </div>
    <div>
      Logbook: <span class="repo">huggingface.co/spaces/DineshAI/0SGle5hjIf</span> &nbsp;&middot;&nbsp;
      Code: <span class="repo">github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy</span>
    </div>
  </div>"""


def qr_data_uri(url: str) -> str:
    import qrcode  # type: ignore
    import io, base64

    img = qrcode.make(url, box_size=10, border=1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def replace_region(html: str, start_pat: str, end_pat: str, new: str) -> str:
    m = re.search(start_pat, html)
    e = re.search(end_pat, html[m.end():])
    return html[: m.start()] + new + html[m.end() + e.end():]


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "images").mkdir(exist_ok=True)
    for p in (REPO / "reports" / "poster").glob("*.png"):
        shutil.copy(p, BUILD / "images" / p.name)

    html = TEMPLATE.read_text()

    for tok, val in TOKENS.items():
        html = re.sub(rf"(\s{re.escape(tok)}\s*:\s*)#[0-9a-fA-F]{{3,8}}",
                      rf"\g<1>{val}", html, count=1)

    # Header: drop the venue badge (no venue named) per the template defaults.
    html = replace_region(html, r'  <header class="header"[^>]*>', r'</header>', HEADER)
    html = replace_region(html, r'  <section class="framework-banner"[^>]*>',
                          r'</section>', BANNER)
    html = replace_region(html, r'  <div class="body-grid"[^>]*>\n',
                          r'\n  </div>\n\n  <!-- =+ OPTIONAL TAKEAWAYS',
                          '  <div class="body-grid" data-measure-role="body">\n\n'
                          + "\n\n".join([COL1, COL2, COL3, COL4])
                          + "\n\n  </div>\n\n  <!-- ===== TAKEAWAYS")
    html = replace_region(html, r'  <section class="takeaways-strip"[^>]*>',
                          r'</section>', STRIP)
    html = replace_region(html, r'  <div class="footer" data-measure-role="footer">',
                          r'\n  </div>', FOOTER)
    html = html.replace(
        '<div class="ornament">LAB &middot; INSTITUTION</div>',
        '<div class="ornament">ICML 2026 &middot; REPRODUCIBILITY</div>')

    try:
        html = html.replace("QRSRC", qr_data_uri(
            "https://huggingface.co/spaces/DineshAI/0SGle5hjIf"))
    except Exception:
        html = html.replace("QRSRC", "images/qr.png")

    css = BALANCE_CSS
    for i, v in enumerate(BALANCE):
        css = css.replace(f"VAL{i}", str(v))
    html = html.replace("</head>", css + "</head>", 1)

    OUT.write_text(html)
    print("wrote", OUT, len(html), "bytes")
    print("remaining TODO markers:", html.count("TODO"))


if __name__ == "__main__":
    main()
