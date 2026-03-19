"""Report generator for The CISO Council.

Responsibilities:
- Call the LLM to produce consensus/dissent/ambiguity analysis
- Format CouncilReport as Markdown and/or JSON
- Save reports to the outputs/ directory

The consensus analysis is itself an LLM call using CONSENSUS_SYSTEM_PROMPT
from prompts.py, so the synthesis is as thoughtful as the debate.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from rich.console import Console

from council.models import (
    AmbiguityInsight,
    ConsensusPoint,
    CouncilReport,
    DissentPoint,
    ScoredResponse,
    Scenario,
)
from council.prompts import CONSENSUS_SYSTEM_PROMPT
from council.providers import get_completion

_console = Console()

_PROJECT_ROOT = Path(__file__).parent.parent


# ─── Consensus Analysis ───────────────────────────────────────────────────────

def _build_consensus_user_prompt(
    scenario: Scenario,
    scored_responses: list[ScoredResponse],
) -> str:
    """Build the user prompt for the consensus/dissent analysis call.

    Args:
        scenario: The debated scenario.
        scored_responses: Scored responses from all council members.

    Returns:
        A user prompt string ready for the scoring/synthesis model.
    """
    lines = [
        f"SCENARIO: {scenario.title}",
        f"DOMAIN: {scenario.domain}",
        "",
        f"DILEMMA: {scenario.dilemma}",
        "",
        "COUNCIL RESPONSES (with scores):",
    ]

    for sr in scored_responses:
        r = sr.response
        if r.error:
            continue
        avg = sr.overall_score
        lines.append(f"\n--- {r.persona_name} ({r.persona_title}) | Overall score: {avg}/10 ---")
        lines.append(r.response_text)

    lines.append("\nAnalyse the responses above. Identify consensus, dissent, and ambiguity as instructed.")
    return "\n".join(lines)


def _parse_analysis_json(text: str) -> dict:
    """Extract and parse JSON from the consensus analysis model response.

    Args:
        text: Raw response text from the synthesis model.

    Returns:
        Parsed analysis dict.
    """
    cleaned = re.sub(r"```(?:json)?", "", text.strip())
    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {}


def _build_fallback_analysis(scored_responses: list[ScoredResponse]) -> dict:
    """Return a minimal analysis when the LLM call fails.

    Args:
        scored_responses: Scored responses from all council members.

    Returns:
        A dict matching the expected consensus analysis structure.
    """
    names = [sr.response.persona_name for sr in scored_responses if not sr.response.error]
    names_str = ", ".join(names) if names else "no members"
    return {
        "consensus": [
            {
                "summary": (
                    "Automated synthesis failed. Review individual responses from: "
                    + names_str + "."
                ),
                "supporting_members": names,
                "confidence": "low",
            }
        ],
        "dissent": [
            {
                "summary": "Synthesis model unavailable — dissent analysis not generated.",
                "dissenting_members": [],
                "majority_position": "See individual responses.",
                "dissent_rationale": "Manual review required.",
            }
        ],
        "ambiguity_analysis": [
            {
                "insight": "Consensus/dissent synthesis failed. Check server logs for details.",
                "contributing_factors": ["Synthesis model call failed or returned invalid JSON"],
            }
        ],
        "top_recommendation": (
            "Automated recommendation unavailable. Review individual council responses "
            "from: " + names_str + "."
        ),
    }


async def generate_consensus_analysis(
    scenario: Scenario,
    scored_responses: list[ScoredResponse],
    provider: str,
    model: str,
    api_key: str,
) -> dict:
    """Run the consensus/dissent/ambiguity analysis via LLM.

    Args:
        scenario: The debated scenario.
        scored_responses: All scored council responses.
        provider: LLM provider for synthesis.
        model: Model identifier.
        api_key: API key for the synthesis provider.

    Returns:
        Dict with keys: consensus, dissent, ambiguity_analysis, top_recommendation.
        Falls back to a minimal structure if the call fails.
    """
    if not api_key:
        return _build_fallback_analysis(scored_responses)

    user_prompt = _build_consensus_user_prompt(scenario, scored_responses)
    messages = [
        {"role": "system", "content": CONSENSUS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        raw = await get_completion(
            provider=provider,
            model=model,
            messages=messages,
            api_key=api_key,
            timeout=90,
            temperature=0.0,
            json_mode=True,
        )
        _console.print(
            f"[dim][CONSENSUS] Raw response ({len(raw)} chars): {raw[:500]!r}[/dim]"
        )
        result = _parse_analysis_json(raw)
        if not result:
            _console.print(
                "[yellow][CONSENSUS] JSON parsed to empty dict — falling back.[/yellow]"
            )
            return _build_fallback_analysis(scored_responses)
        return result
    except Exception as exc:
        _console.print(
            f"[red][CONSENSUS] Failed: {type(exc).__name__}: {exc}[/red]"
        )
        return _build_fallback_analysis(scored_responses)


# ─── Formatters ───────────────────────────────────────────────────────────────

def format_markdown(report: CouncilReport) -> str:
    """Format a CouncilReport as a structured Markdown document.

    Args:
        report: The completed council report.

    Returns:
        Markdown string.
    """
    s = report.scenario
    ts = report.timestamp.strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        f"# The CISO Council: {s.title}",
        "",
        f"**Session ID:** {report.session_id}  ",
        f"**Date:** {ts}  ",
        f"**Domain:** {s.domain.replace('_', ' ').title()}  ",
        f"**Council members:** {len(report.responses)}",
        "",
        "---",
        "",
        "## Scenario",
        "",
        s.context,
        "",
        f"**The Dilemma:** {s.dilemma}",
    ]

    if s.constraints:
        lines += ["", "**Constraints:**"]
        lines += [f"- {c}" for c in s.constraints]

    if s.stakeholders:
        lines += ["", "**Stakeholders:**"]
        lines += [f"- {st}" for st in s.stakeholders]

    lines += ["", "---", "", "## Top Recommendation", ""]
    lines.append(f"> {report.top_recommendation}")

    # Consensus
    if report.consensus:
        lines += ["", "---", "", "## Council Consensus", ""]
        for i, cp in enumerate(report.consensus, 1):
            conf_badge = {"high": "HIGH", "moderate": "MODERATE", "low": "LOW"}.get(
                cp.confidence, cp.confidence.upper()
            )
            members_str = ", ".join(cp.supporting_members)
            lines += [
                f"### {i}. {cp.summary}",
                "",
                f"**Confidence:** {conf_badge}  ",
                f"**Supporting:** {members_str}",
                "",
            ]

    # Dissent
    if report.dissent:
        lines += ["---", "", "## Points of Dissent", ""]
        for i, dp in enumerate(report.dissent, 1):
            dissenting = ", ".join(dp.dissenting_members)
            lines += [
                f"### {i}. {dp.summary}",
                "",
                f"**Dissenting:** {dissenting}  ",
                f"**Majority position:** {dp.majority_position}  ",
                f"**Rationale for dissent:** {dp.dissent_rationale}",
                "",
            ]

    # Ambiguity analysis
    if report.ambiguity_analysis:
        lines += ["---", "", "## Ambiguity Analysis", "", "_What the disagreements reveal_", ""]
        for i, ai in enumerate(report.ambiguity_analysis, 1):
            lines.append(f"**{i}. {ai.insight}**")
            if ai.contributing_factors:
                lines += [f"- {f}" for f in ai.contributing_factors]
            lines.append("")

    # Individual responses
    lines += ["---", "", "## Individual Responses", ""]
    for sr in report.responses:
        r = sr.response
        lines += [
            f"### {r.persona_name} — {r.persona_title}",
            f"_Provider: {r.provider} / {r.model} | Latency: {r.latency_seconds:.1f}s_",
            "",
        ]
        if r.error:
            lines += [f"> **Error:** {r.error}", ""]
        else:
            lines += [r.response_text, ""]

        if sr.scores and not r.error:
            lines += ["**Scores:**", ""]
            lines += ["| Dimension | Score | Rationale |", "|---|---|---|"]
            for sc in sr.scores:
                dim = sc.dimension.replace("_", " ").title()
                lines.append(f"| {dim} | {sc.score:.1f}/10 | {sc.rationale} |")
            lines += [
                "",
                f"**Overall: {sr.overall_score:.1f}/10**",
                "",
            ]

    # Risk appetite distribution
    if report.risk_appetite_distribution:
        lines += ["---", "", "## Risk Appetite Distribution", ""]
        for appetite, count in report.risk_appetite_distribution.items():
            if count > 0:
                label = appetite.replace("_", " ").title()
                bar = "█" * count
                lines.append(f"- **{label}:** {bar} ({count})")
        lines.append("")

    # Metadata
    lines += ["---", "", "## Session Metadata", ""]
    meta = report.metadata
    if meta.get("providers_used"):
        lines.append(f"- **Providers:** {', '.join(meta['providers_used'])}")
    if meta.get("total_latency_seconds") is not None:
        lines.append(f"- **Total latency:** {meta['total_latency_seconds']}s")
    if meta.get("concurrent") is not None:
        lines.append(f"- **Mode:** {'Concurrent' if meta['concurrent'] else 'Sequential'}")
    lines += ["", "_Generated by The CISO Council — GRC + AI Series_"]

    return "\n".join(lines)


def format_json(report: CouncilReport) -> str:
    """Format a CouncilReport as a pretty-printed JSON string.

    Args:
        report: The completed council report.

    Returns:
        JSON string with 2-space indentation.
    """
    return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)


# ─── File I/O ─────────────────────────────────────────────────────────────────

def save_report(
    report: CouncilReport,
    output_dir: Path | None = None,
    fmt: str = "both",
) -> list[Path]:
    """Save a report to disk in the configured format(s).

    Args:
        report: The completed council report.
        output_dir: Directory to write files to. Defaults to outputs/.
        fmt: Output format: 'markdown', 'json', or 'both'.

    Returns:
        List of Paths to the files that were written.
    """
    base_dir = output_dir or (_PROJECT_ROOT / "outputs")
    base_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "_", report.scenario.title.lower()).strip("_")
    stem = f"{ts}_{report.session_id}_{slug}"

    written: list[Path] = []

    if fmt in ("markdown", "both"):
        md_path = base_dir / f"{stem}.md"
        md_path.write_text(format_markdown(report), encoding="utf-8")
        written.append(md_path)

    if fmt in ("json", "both"):
        json_path = base_dir / f"{stem}.json"
        json_path.write_text(format_json(report), encoding="utf-8")
        written.append(json_path)

    return written


def load_latest_report(output_dir: Path | None = None) -> dict | None:
    """Load the most recently saved JSON report from outputs/.

    Args:
        output_dir: Directory to search. Defaults to outputs/.

    Returns:
        Parsed JSON dict, or None if no reports exist.
    """
    base_dir = output_dir or (_PROJECT_ROOT / "outputs")
    json_files = sorted(base_dir.glob("*.json"), reverse=True)
    if not json_files:
        return None
    with open(json_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def load_latest_markdown_path(output_dir: Path | None = None) -> Path | None:
    """Return the path to the most recently saved Markdown report.

    Args:
        output_dir: Directory to search. Defaults to outputs/.

    Returns:
        Path to the latest .md file, or None if none exist.
    """
    base_dir = output_dir or (_PROJECT_ROOT / "outputs")
    md_files = sorted(base_dir.glob("*.md"), reverse=True)
    return md_files[0] if md_files else None
