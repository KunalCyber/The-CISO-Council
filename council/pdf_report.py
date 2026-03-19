"""PDF report generator for The CISO Council.

Produces a board-ready A4 PDF using ReportLab's Platypus framework.
All fonts are Helvetica (built-in, no external files required).

Entry point: generate_pdf_report(report_data, output_path)
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Colour palette ───────────────────────────────────────────────────────────

NAVY        = HexColor('#1B2A4A')
VIOLET      = HexColor('#7C3AED')
VIOLET_PALE = HexColor('#EDE9FE')
DARK        = HexColor('#1A1A1A')
BODY        = HexColor('#2D2D2D')
MID         = HexColor('#64748B')
LIGHT       = HexColor('#F1F5F9')
RULE        = HexColor('#E2E8F0')
WHITE       = colors.white

# ─── Risk appetite labels ─────────────────────────────────────────────────────

_APPETITE_LABELS = {
    1: "Ultra-Conservative",
    2: "Conservative",
    3: "Moderate",
    4: "Tolerant",
    5: "Aggressive",
}


# ─── Styles ───────────────────────────────────────────────────────────────────

def _build_styles() -> dict[str, ParagraphStyle]:
    def S(name: str, **kw) -> ParagraphStyle:
        return ParagraphStyle(name=name, **kw)

    return {
        # Cover
        "cover_title": S(
            "cover_title",
            fontName="Helvetica-Bold", fontSize=36, leading=44,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_sub": S(
            "cover_sub",
            fontName="Helvetica", fontSize=15, leading=20,
            textColor=MID, alignment=TA_CENTER, spaceAfter=4,
        ),
        "cover_scenario": S(
            "cover_scenario",
            fontName="Helvetica-Bold", fontSize=19, leading=26,
            textColor=DARK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_meta": S(
            "cover_meta",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=MID, alignment=TA_CENTER, spaceAfter=3,
        ),
        "cover_confidential": S(
            "cover_confidential",
            fontName="Helvetica-BoldOblique", fontSize=9, leading=12,
            textColor=MID, alignment=TA_CENTER,
        ),
        # Section headings
        "h1": S(
            "h1",
            fontName="Helvetica-Bold", fontSize=20, leading=26,
            textColor=NAVY, spaceBefore=0, spaceAfter=10,
        ),
        "h2": S(
            "h2",
            fontName="Helvetica-Bold", fontSize=13, leading=18,
            textColor=NAVY, spaceBefore=16, spaceAfter=6,
        ),
        "h3": S(
            "h3",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=DARK, spaceBefore=8, spaceAfter=3,
        ),
        # Body text
        "body": S(
            "body",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "body_large": S(
            "body_large",
            fontName="Helvetica", fontSize=12, leading=18,
            textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        "label": S(
            "label",
            fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=MID, spaceAfter=2,
        ),
        "footnote": S(
            "footnote",
            fontName="Helvetica-Oblique", fontSize=8, leading=11,
            textColor=MID, spaceAfter=4,
        ),
        # Member sections
        "member_name": S(
            "member_name",
            fontName="Helvetica-Bold", fontSize=13, leading=17,
            textColor=NAVY, spaceAfter=2, spaceBefore=4,
        ),
        "member_sub": S(
            "member_sub",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=MID, spaceAfter=8,
        ),
        # Consensus / dissent
        "numbered_item": S(
            "numbered_item",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=4,
            leftIndent=14,
        ),
        "item_meta": S(
            "item_meta",
            fontName="Helvetica-Oblique", fontSize=9, leading=12,
            textColor=MID, spaceAfter=10, leftIndent=14,
        ),
        "dissent_label": S(
            "dissent_label",
            fontName="Helvetica-Bold", fontSize=9, leading=12,
            textColor=DARK, spaceAfter=2, leftIndent=14,
        ),
    }


# ─── Footer canvas ────────────────────────────────────────────────────────────

class _FooterCanvas(rl_canvas.Canvas):
    """Draws a footer on every page except page 1 (the cover)."""

    def __init__(self, *args, **kwargs):
        rl_canvas.Canvas.__init__(self, *args, **kwargs)
        self._page_buffer: list[dict] = []

    def showPage(self):
        self._page_buffer.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._page_buffer)
        for i, state in enumerate(self._page_buffer, start=1):
            self.__dict__.update(state)
            if i > 1:
                self._draw_footer(i, total)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _draw_footer(self, page_num: int, total_pages: int) -> None:
        page_w, _ = A4
        margin = 25 * mm
        y_line = 16 * mm
        y_text = 10 * mm
        self.saveState()
        self.setStrokeColor(VIOLET)
        self.setLineWidth(0.6)
        self.line(margin, y_line, page_w - margin, y_line)
        self.setFont("Helvetica", 8)
        self.setFillColor(MID)
        self.drawString(margin, y_text, "The CISO Council  |  Kunal RK")
        self.drawRightString(
            page_w - margin, y_text, f"Page {page_num} of {total_pages}"
        )
        self.restoreState()


# ─── Helper: violet accent rule ───────────────────────────────────────────────

def _accent_rule() -> HRFlowable:
    return HRFlowable(
        width="100%", thickness=1.5, color=VIOLET, spaceAfter=4, spaceBefore=4
    )


def _thin_rule() -> HRFlowable:
    return HRFlowable(
        width="100%", thickness=0.5, color=RULE, spaceAfter=6, spaceBefore=6
    )


# ─── Cover page ───────────────────────────────────────────────────────────────

def _build_cover(report: dict, styles: dict) -> list:
    scenario = report.get("scenario", {})
    session_id = report.get("session_id", "")
    ts_raw = report.get("timestamp", "")
    try:
        ts = datetime.fromisoformat(ts_raw).strftime("%d %B %Y")
    except Exception:
        ts = ts_raw[:10] if ts_raw else ""

    domain = scenario.get("domain", "").replace("_", " ").title()

    elems: list = [
        Spacer(1, 52 * mm),
        Paragraph("THE CISO COUNCIL", styles["cover_title"]),
        Paragraph("Council Session Report", styles["cover_sub"]),
        Spacer(1, 10 * mm),
        HRFlowable(width="50%", thickness=2, color=VIOLET, hAlign="CENTER"),
        Spacer(1, 10 * mm),
        Paragraph(scenario.get("title", ""), styles["cover_scenario"]),
        Spacer(1, 6 * mm),
        Paragraph(f"Domain: {domain}", styles["cover_meta"]),
        Paragraph(f"Date: {ts}", styles["cover_meta"]),
        Paragraph(f"Session ID: {session_id}", styles["cover_meta"]),
        Spacer(1, 62 * mm),
        HRFlowable(width="100%", thickness=0.5, color=RULE, hAlign="CENTER"),
        Spacer(1, 5 * mm),
        Paragraph("CONFIDENTIAL", styles["cover_confidential"]),
        PageBreak(),
    ]
    return elems


# ─── Executive summary ────────────────────────────────────────────────────────

def _build_exec_summary(report: dict, styles: dict, page_w: float) -> list:
    usable = page_w - 50 * mm  # margins each side

    elems: list = [
        Paragraph("Executive Summary", styles["h1"]),
        _accent_rule(),
        Spacer(1, 4 * mm),
    ]

    # Chief arbiter recommendation
    rec = report.get("top_recommendation", "").strip()
    if rec:
        elems.append(Paragraph("Chief Arbiter Recommendation", styles["h2"]))
        elems.append(Paragraph(rec, styles["body_large"]))
        elems.append(Spacer(1, 4 * mm))

    # Council members summary table
    responses = report.get("responses", [])
    if responses:
        elems.append(Paragraph("Council Members — Score Summary", styles["h2"]))
        elems.append(Spacer(1, 2 * mm))

        col_name  = usable * 0.30
        col_title = usable * 0.32
        col_score = usable * 0.18
        col_model = usable * 0.20

        header = [
            Paragraph("<b>Member</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("<b>Role</b>",   ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
            Paragraph("<b>Score</b>",  ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph("<b>Model</b>",  ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)),
        ]
        rows = [header]
        for sr in responses:
            r = sr.get("response", {})
            overall = sr.get("overall_score", 0)
            score_text = f"{overall:.1f} / 10" if overall > 0 else "N/A"
            rows.append([
                Paragraph(r.get("persona_name", ""), ParagraphStyle("tc", fontName="Helvetica", fontSize=9, textColor=DARK)),
                Paragraph(r.get("persona_title", ""), ParagraphStyle("tc", fontName="Helvetica", fontSize=9, textColor=DARK)),
                Paragraph(score_text, ParagraphStyle("tc", fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, alignment=TA_CENTER)),
                Paragraph(f"{r.get('provider','')}/{r.get('model','')}", ParagraphStyle("tc", fontName="Helvetica", fontSize=8, textColor=MID)),
            ])

        tbl = Table(rows, colWidths=[col_name, col_title, col_score, col_model])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  NAVY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT]),
            ("GRID",         (0, 0), (-1, -1),  0.4, RULE),
            ("TOPPADDING",   (0, 0), (-1, -1),  5),
            ("BOTTOMPADDING",(0, 0), (-1, -1),  5),
            ("LEFTPADDING",  (0, 0), (-1, -1),  6),
            ("RIGHTPADDING", (0, 0), (-1, -1),  6),
            ("VALIGN",       (0, 0), (-1, -1),  "MIDDLE"),
        ]))
        elems.append(tbl)
        elems.append(Spacer(1, 3 * mm))
        elems.append(Paragraph(
            "Scores produced by Gemini 2.5 Flash on five GRC dimensions: "
            "Regulatory Defensibility, Practicality, Board-Readiness, "
            "Specificity, and Risk Quantification.",
            styles["footnote"],
        ))

    elems.append(PageBreak())
    return elems


# ─── Individual council responses ─────────────────────────────────────────────

def _score_bar_table(scores: list[dict], usable: float) -> Table:
    """Compact two-column score table: dimension | score | rationale."""
    col_dim  = usable * 0.28
    col_scr  = usable * 0.10
    col_rat  = usable * 0.62

    cell_style = ParagraphStyle("sc", fontName="Helvetica", fontSize=8, textColor=DARK, leading=11)
    dim_style  = ParagraphStyle("sd", fontName="Helvetica-Bold", fontSize=8, textColor=DARK, leading=11)
    scr_style  = ParagraphStyle("ss", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, leading=11, alignment=TA_CENTER)

    header = [
        Paragraph("<b>Dimension</b>",  ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)),
        Paragraph("<b>Score</b>",       ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("<b>Rationale</b>",   ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)),
    ]
    rows = [header]
    for sc in scores:
        dim = sc.get("dimension", "").replace("_", " ").title()
        score = sc.get("score", 0)
        score_txt = f"{score:.0f}/10" if score > 0 else "—"
        rows.append([
            Paragraph(dim, dim_style),
            Paragraph(score_txt, scr_style),
            Paragraph(sc.get("rationale", ""), cell_style),
        ])

    tbl = Table(rows, colWidths=[col_dim, col_scr, col_rat])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID",          (0, 0), (-1, -1),  0.3, RULE),
        ("TOPPADDING",    (0, 0), (-1, -1),  4),
        ("BOTTOMPADDING", (0, 0), (-1, -1),  4),
        ("LEFTPADDING",   (0, 0), (-1, -1),  5),
        ("RIGHTPADDING",  (0, 0), (-1, -1),  5),
        ("VALIGN",        (0, 0), (-1, -1),  "TOP"),
    ]))
    return tbl


def _build_responses(report: dict, styles: dict, usable: float) -> list:
    elems: list = [
        Paragraph("Individual Council Responses", styles["h1"]),
        _accent_rule(),
        Spacer(1, 4 * mm),
    ]

    responses = report.get("responses", [])
    try:
        from council.personas import get_persona
        personas_available = True
    except Exception:
        personas_available = False

    for idx, sr in enumerate(responses):
        r = sr.get("response", {})
        scores = sr.get("scores", [])
        overall = sr.get("overall_score", 0)
        persona_id = r.get("persona_id", "")

        # Risk appetite from persona registry if available
        appetite_str = ""
        if personas_available and persona_id:
            try:
                p = get_persona(persona_id)
                label = _APPETITE_LABELS.get(p.risk_appetite.value, "")
                appetite_str = f"Risk Appetite: {p.risk_appetite.value}/5  —  {label}  |  {p.org_context.sector.title()}, {p.org_context.size.title()}"
            except Exception:
                pass

        overall_display = f"Overall: {overall:.1f}/10" if overall > 0 else "Scoring unavailable"

        # Member header block — keep together
        header_block: list = [
            _thin_rule() if idx > 0 else Spacer(1, 1),
            Paragraph(r.get("persona_name", ""), styles["member_name"]),
            Paragraph(
                f"{r.get('persona_title', '')}  |  {overall_display}",
                styles["member_sub"],
            ),
        ]
        if appetite_str:
            header_block.append(Paragraph(appetite_str, styles["member_sub"]))

        elems.extend(header_block)

        # Response body
        if r.get("error"):
            elems.append(Paragraph(
                f"Error: {r['error']}",
                ParagraphStyle("err", fontName="Helvetica-Oblique", fontSize=9, textColor=colors.red),
            ))
        else:
            # Split into paragraphs on double newline; single newlines become spaces
            raw_text = r.get("response_text", "").strip()
            paragraphs = [p.replace("\n", " ").strip() for p in raw_text.split("\n\n") if p.strip()]
            for para in paragraphs:
                elems.append(Paragraph(para, styles["body"]))

        # Score table
        valid_scores = [s for s in scores if s.get("score", 0) > 0]
        if valid_scores:
            elems.append(Spacer(1, 3 * mm))
            elems.append(_score_bar_table(valid_scores, usable))

        elems.append(Spacer(1, 4 * mm))

    elems.append(PageBreak())
    return elems


# ─── Consensus and dissent ────────────────────────────────────────────────────

def _build_consensus_dissent(report: dict, styles: dict) -> list:
    elems: list = [
        Paragraph("Council Consensus &amp; Dissent", styles["h1"]),
        _accent_rule(),
    ]

    consensus = report.get("consensus", [])
    if consensus:
        elems.append(Paragraph("Points of Consensus", styles["h2"]))
        for i, pt in enumerate(consensus, 1):
            conf = pt.get("confidence", "").capitalize()
            members = ", ".join(pt.get("supporting_members", []))
            elems.append(Paragraph(
                f"{i}.  {pt.get('summary', '')}",
                styles["numbered_item"],
            ))
            if members or conf:
                meta = f"Supporting: {members}" if members else ""
                if conf:
                    meta += f"  |  Confidence: {conf}" if meta else f"Confidence: {conf}"
                elems.append(Paragraph(meta, styles["item_meta"]))

    dissent = report.get("dissent", [])
    if dissent:
        elems.append(Spacer(1, 4 * mm))
        elems.append(Paragraph("Dissenting Views", styles["h2"]))
        for i, pt in enumerate(dissent, 1):
            dissenters = ", ".join(pt.get("dissenting_members", []))
            summary = pt.get("summary", "")
            majority = pt.get("majority_position", "")
            rationale = pt.get("dissent_rationale", "")

            if dissenters:
                elems.append(Paragraph(f"{i}.  {summary}", styles["numbered_item"]))
                elems.append(Paragraph(f"Dissenting: {dissenters}", styles["dissent_label"]))
                if majority:
                    elems.append(Paragraph(f"Majority position: {majority}", styles["item_meta"]))
                if rationale:
                    elems.append(Paragraph(f"Rationale: {rationale}", styles["item_meta"]))
            else:
                elems.append(Paragraph(f"{i}.  {summary}", styles["numbered_item"]))
                elems.append(Spacer(1, 2 * mm))

    elems.append(PageBreak())
    return elems


# ─── Ambiguity analysis ───────────────────────────────────────────────────────

def _build_ambiguity(report: dict, styles: dict) -> list:
    insights = report.get("ambiguity_analysis", [])
    if not insights:
        return []

    elems: list = [
        Paragraph("Ambiguity Analysis", styles["h1"]),
        _accent_rule(),
        Paragraph(
            "What the council's disagreements reveal about the decision's inherent complexity.",
            styles["body"],
        ),
        Spacer(1, 4 * mm),
    ]

    for i, ai in enumerate(insights, 1):
        insight = ai.get("insight", "").strip()
        factors = ai.get("contributing_factors", [])
        if not insight:
            continue
        elems.append(Paragraph(f"{i}.  {insight}", styles["numbered_item"]))
        if factors:
            factors_str = "  ·  ".join(factors)
            elems.append(Paragraph(
                f"Contributing factors: {factors_str}",
                styles["item_meta"],
            ))

    return elems


# ─── Public entry point ───────────────────────────────────────────────────────

def generate_pdf_report(report_data: dict, output_path: str | Path | None = None) -> bytes:
    """Generate a board-ready PDF from a CouncilReport dict.

    Args:
        report_data: The session report as a dict (from model_dump or JSON load).
        output_path: If provided, also writes the PDF to this path.

    Returns:
        PDF content as bytes.
    """
    page_w, page_h = A4
    margin = 25 * mm
    usable = page_w - 2 * margin

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=28 * mm,  # extra space for footer
        title=f"The CISO Council — {report_data.get('scenario', {}).get('title', 'Report')}",
        author="The CISO Council",
        subject="Council Session Report",
    )

    styles = _build_styles()

    story: list = []
    story.extend(_build_cover(report_data, styles))
    story.extend(_build_exec_summary(report_data, styles, page_w))
    story.extend(_build_responses(report_data, styles, usable))
    story.extend(_build_consensus_dissent(report_data, styles))
    story.extend(_build_ambiguity(report_data, styles))

    doc.build(story, canvasmaker=_FooterCanvas)

    pdf_bytes = buf.getvalue()

    if output_path:
        Path(output_path).write_bytes(pdf_bytes)

    return pdf_bytes
