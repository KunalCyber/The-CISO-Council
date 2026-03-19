"""Multi-dimensional scoring engine for The CISO Council.

Each council member's response is scored on five GRC-relevant dimensions
by a separate LLM call (default: Gemini Flash, fast and free).

Scoring dimensions:
- regulatory_defensibility
- practicality
- board_readiness
- specificity
- risk_quantification
"""

from __future__ import annotations

import json
import re

from rich.console import Console

from council.models import (
    CouncilResponse,
    DimensionScore,
    Persona,
    Scenario,
    ScoredResponse,
)
from council.prompts import SCORING_SYSTEM_PROMPT, build_scoring_user_prompt
from council.providers import get_completion

console = Console()


def _parse_scoring_json(text: str) -> dict:
    """Extract and parse the JSON block from a scoring model response.

    The model may wrap JSON in markdown code fences; this strips them.

    Args:
        text: Raw response text from the scoring model.

    Returns:
        Parsed JSON as a dict.

    Raises:
        ValueError: If no valid JSON can be extracted.
    """
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r"```(?:json)?", "", text.strip())
    cleaned = cleaned.replace("```", "").strip()

    # Try direct parse first.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find the outermost JSON object in the text.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from scoring response: {text[:300]!r}")


def _compute_overall(scores: list[DimensionScore]) -> float:
    """Compute the mean score across all dimensions.

    Args:
        scores: List of dimension scores.

    Returns:
        Mean score, rounded to two decimal places.
    """
    if not scores:
        return 0.0
    return round(sum(s.score for s in scores) / len(scores), 2)


async def score_response(
    scenario: Scenario,
    persona: Persona,
    response: CouncilResponse,
    scoring_provider: str,
    scoring_model: str,
    api_key: str,
) -> ScoredResponse:
    """Score a council member's response on all GRC dimensions.

    Makes a single LLM call to a scoring model and parses the structured
    JSON output. Falls back to neutral scores (5.0) if parsing fails.

    Args:
        scenario: The scenario that was debated.
        persona: The persona that produced the response.
        response: The council member's response.
        scoring_provider: LLM provider to use for scoring.
        scoring_model: Model identifier for the scoring provider.
        api_key: API key for the scoring provider.

    Returns:
        A ScoredResponse with dimension scores and an overall score.
    """
    # If the original response errored, skip scoring and show zeros.
    if response.error:
        console.print(
            f"[yellow][SCORING] Skipping {persona.name} — response had error: {response.error}[/yellow]"
        )
        fallback_scores = _fallback_scores(note=f"Response error: {response.error}")
        return ScoredResponse(
            response=response,
            scores=fallback_scores,
            overall_score=_compute_overall(fallback_scores),
        )

    user_prompt = build_scoring_user_prompt(scenario, persona, response.response_text)
    messages = [
        {"role": "system", "content": SCORING_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    console.print(
        f"[dim][SCORING] Calling {scoring_provider}/{scoring_model} for {persona.name} "
        f"(response length: {len(response.response_text)} chars)[/dim]"
    )

    try:
        raw = await get_completion(
            provider=scoring_provider,
            model=scoring_model,
            messages=messages,
            api_key=api_key,
            timeout=60,
            temperature=0.0,
            json_mode=True,
        )
        console.print(
            f"[dim][SCORING] Raw response for {persona.name} "
            f"({len(raw)} chars):\n{raw}[/dim]"
        )
        parsed = _parse_scoring_json(raw)
        console.print(f"[dim][SCORING] Parsed for {persona.name}: {parsed}[/dim]")
        scores = _parse_dimension_scores(parsed)
        if scores:
            score_summary = ", ".join(f"{s.dimension}={s.score}" for s in scores)
            console.print(f"[green][SCORING] {persona.name}: {score_summary}[/green]")
        else:
            console.print(
                f"[yellow][SCORING] Parsed JSON but extracted no scores for {persona.name}. "
                f"Full parsed: {parsed}[/yellow]"
            )
    except Exception as exc:
        console.print(
            f"[red][SCORING] Failed for {persona.name}: {type(exc).__name__}: {exc}[/red]"
        )
        # Scoring failure should not abort the session.
        scores = _fallback_scores(note=f"Scoring failed: {type(exc).__name__}: {exc}")

    overall = _compute_overall(scores)
    return ScoredResponse(response=response, scores=scores, overall_score=overall)


def _parse_dimension_scores(parsed: dict) -> list[DimensionScore]:
    """Convert parsed JSON into DimensionScore objects.

    Args:
        parsed: Parsed scoring JSON from the model.

    Returns:
        List of DimensionScore objects.
    """
    scores: list[DimensionScore] = []
    for item in parsed.get("scores", []):
        try:
            raw_score = float(item.get("score", 0))
            clamped = max(0.0, min(10.0, raw_score))
            scores.append(
                DimensionScore(
                    dimension=item.get("dimension", "unknown"),
                    score=clamped,
                    rationale=item.get("rationale", ""),
                )
            )
        except (TypeError, ValueError):
            continue
    return scores if scores else _fallback_scores()


def _fallback_scores(note: str = "Scoring failed") -> list[DimensionScore]:
    """Return zero scores for all five dimensions when scoring fails.

    Used when scoring fails so the session can still produce a report.
    Returns 0 rather than a fake neutral score so the failure is visible.

    Args:
        note: Rationale to attach to each score.

    Returns:
        List of five DimensionScore objects each with score 0.0.
    """
    dimensions = [
        "regulatory_defensibility",
        "practicality",
        "board_readiness",
        "specificity",
        "risk_quantification",
    ]
    return [
        DimensionScore(dimension=d, score=0.0, rationale=note)
        for d in dimensions
    ]
