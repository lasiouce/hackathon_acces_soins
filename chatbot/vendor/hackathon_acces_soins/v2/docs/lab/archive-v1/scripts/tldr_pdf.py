"""One-page TL;DR of the project so far -> docs/lab/presentations/2026-11-13-tldr.pdf
Run: uv run --with reportlab python scripts/tldr_pdf.py
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

F = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", F + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", F + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", F + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

INK, MUTED, ACCENT, RED, LINE = (colors.HexColor(c) for c in ("#1a1a1a", "#666666", "#1f4e79", "#a8322d", "#d0d7de"))
body = ParagraphStyle("b", fontName="Arial", fontSize=8.6, leading=11, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=7.6, leading=9.6, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=body, fontName="Arial-Bold", fontSize=15, leading=18, textColor=ACCENT)
h2 = ParagraphStyle("h2", parent=body, fontName="Arial-Bold", fontSize=9.6, leading=12, textColor=ACCENT, spaceBefore=6, spaceAfter=2)
lead = ParagraphStyle("lead", parent=body, fontSize=9.6, leading=12.6)

P = lambda t, s=body: Paragraph(t, s)


def table(rows, widths, header=True):
    rows = [[f'<b>{c}</b>' for c in rows[0]]] + rows[1:] if header else rows
    t = Table([[P(c) if isinstance(c, str) else c for c in r] for r in rows], colWidths=widths)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
          ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f8"))]
    t.setStyle(TableStyle(st))
    return t


W = A4[0] - 30 * mm
story = [
    P("Health workforce twin: status after day 1", h1),
    P("Hackathon santé · projecting MMOPKSI professionals (excluding general practice) by territory, "
      "with policy scenarios · open data only · 13 Nov 2026", small),
    Spacer(1, 6),
    P("<b>TL;DR.</b> We chose the model form: a <b>stock-flow model by age, sex, profession and département</b>, "
      "measured against a “nothing changes” baseline. Every policy lever acts on one of <b>7 flow terms</b>, which "
      "is how we cover policy levers exhaustively. A full recompute takes about <b>1 ms</b>, so the demo can update "
      "live. Key derived finding: <b>quotas cannot change the 2035 specialist count</b>. Training takes about 10 years "
      "and 2035 is 9 years away, so every future specialist is already a student. The data we hold covers the "
      "<b>student pipeline only</b>; <font color='#a8322d'><b>the stock of working professionals is missing and "
      "blocks the model</b></font>.", lead),

    P("What we did", h2),
    table([
        ["Step", "Output", "Result"],
        ["Set up the project", "Repo, Python env (uv), lab profile, records", "Headline = decision usefulness <b>and</b> backtest error · budget 480 person-hours"],
        ["Derived the model", "derivations/workforce-projection-model", "Stock-flow (H1) promoted · baseline (H0) · behavioural installation parked · ML / agent-based killed"],
        ["Inventoried the data", "schema-only report of 8 xlsx (no rows read) → explorations/data-inventory", "Students M/O/P by year × site × region, 2020–2025: <b>have</b> · SIES 2025 entry flows: <b>have</b> · <font color='#a8322d'><b>stock: missing</b></font>"],
        ["Organised the work", "Obsidian vault: Home, filterable records, templates, status deck", "Every analysis = one note with a numeric headline"],
    ], [W * .2, W * .36, W * .44]),

    P("Key numbers (all derived, not yet measured)", h2),
    table([
        ["Claim", "Value", "Basis"],
        ["Effect of quotas on 2035 specialists", "≈ 0", "Training ≈ 10 y > 9 y horizon"],
        ["Effect of +10 % nursing quota on 2035 stock", "≈ +1.7 %", "0.1 × (9 − 3) / 35; career length 35 y assumed"],
        ["Long-run stock", "N* = quota × career length", "Little's law"],
        ["Recompute time", "≈ 1 ms", "6 professions × 101 dép × 45 ages × 2 sexes × 15 y ≈ 10<super>6</super> operations"],
        ["Smallest reliable territory", "département (region if N < ~30)", "Poisson noise ≈ 1/√N: N = 5 gives ±45 %"],
    ], [W * .38, W * .24, W * .38]),

    P("Flagged: what could make this wrong", h2),
    P("• Nothing is measured yet. Training lengths and the 35-year career are assumptions. "
      "• “DES Médecine” includes general practice, which the brief excludes, so we can't separate specialists without the posts by specialty. "
      "• There is no regional data for sages-femmes, kinés or infirmiers. "
      "• DREES likely already publishes projections and an access indicator (APL); we must cite them before claiming anything is new.", body),

    P("Implications", h2),
    P("• For a question like “Clermont 2035”, the demo should lead with <b>retention, where graduates settle, "
      "foreign diplomas and task shifting</b>; quotas are a long-run lever. "
      "• The student data already allows the “are quotas locked?” check (K2) with real numbers. "
      "• If a Mistral model is required, it turns a plain-language question into lever settings; it never does the forecast.", body),

    P("Next, with costs", h2),
    table([
        ["#", "Action", "Cost", "Unblocks"],
        ["1", "Get the DREES stock by profession × age × sex × département, max years", "~1 h", "the model (H1) and the backtest (K1)"],
        ["2", "Internship posts by specialty (separate specialists from GPs)", "~30 min", "scope compliance"],
        ["3", "Enrolments at nursing, kiné and midwifery schools by region · Insee projections", "~1 h", "entries for S/K/I · need side"],
        ["4", "Decide: horizon 2035? département level? headcount or FTE? Mistral required?", "15 min, team", "the demo"],
    ], [W * .05, W * .55, W * .13, W * .27]),
]

out = "docs/lab/presentations/2026-11-13-tldr.pdf"
SimpleDocTemplate(out, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=13 * mm, bottomMargin=12 * mm,
                  title="Health workforce twin: status day 1", author="hackathon-sante").build(story)
print(out)
