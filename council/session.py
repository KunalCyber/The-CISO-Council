"""Council session orchestrator for The CISO Council.

Manages the full lifecycle of a council debate:
1. Load config and scenario
2. Collect responses from each council member (sequential or concurrent)
3. Score each response
4. Run consensus/dissent analysis
5. Return a structured CouncilReport

Designed for graceful degradation: if one provider is down,
the session continues with the remaining members.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from council.config import Config, MemberConfig, get_api_key, load_config
from council.models import (
    CouncilReport,
    CouncilResponse,
    Persona,
    RiskAppetite,
    Scenario,
    ScoredResponse,
)
from council.personas import PERSONAS, get_persona
from council.providers import get_completion
from council.prompts import build_persona_system_prompt, build_scenario_user_prompt
from council.scenarios import load_scenario
from council.scoring import score_response

console = Console()


class CouncilSession:
    """Orchestrates a full council session from scenario to report.

    Args:
        config: Loaded configuration object. If None, loads from disk.
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()

    async def run(
        self,
        scenario_path: str | Path | None = None,
        scenario: Scenario | None = None,
        members: list[str] | None = None,
    ) -> CouncilReport:
        """Run a complete council session.

        Args:
            scenario_path: Path to the scenario YAML file. Mutually exclusive
                with scenario.
            scenario: A pre-built Scenario object. Use this when the scenario
                is not stored on disk (e.g. custom user input).
            members: Optional list of persona IDs to include. If None,
                uses all enabled members from config.

        Returns:
            A fully populated CouncilReport.

        Raises:
            ValueError: If neither scenario_path nor scenario is provided,
                or if no council members are active.
        """
        if scenario is None:
            if scenario_path is None:
                raise ValueError("Provide either scenario_path or scenario.")
            scenario = load_scenario(scenario_path)
        session_id = f"CS-{uuid.uuid4().hex[:8].upper()}"
        active_members = self._resolve_members(members)

        if not active_members:
            raise ValueError(
                "No council members are active. Check config.yaml and that "
                "at least one provider has a valid API key."
            )

        console.print(f"\n[bold yellow]THE CISO COUNCIL[/bold yellow] [dim]Session {session_id}[/dim]")
        console.print(f"[dim]Scenario:[/dim] [bold]{scenario.title}[/bold]")
        console.print(f"[dim]Council members:[/dim] {len(active_members)}\n")

        # Collect responses.
        if self.config.session.concurrent:
            responses = await self._collect_concurrent(scenario, active_members)
        else:
            responses = await self._collect_sequential(scenario, active_members)

        # Score each response.
        scored = await self._score_all(scenario, active_members, responses)

        # Generate consensus/dissent analysis.
        from council.report import generate_consensus_analysis
        analysis = await generate_consensus_analysis(
            scenario=scenario,
            scored_responses=scored,
            provider=self.config.scoring.provider,
            model=self.config.scoring.model,
            api_key=get_api_key(self.config.scoring.provider) or "",
        )

        risk_dist = self._risk_distribution(active_members)
        total_latency = sum(r.latency_seconds for r in responses)

        report = CouncilReport(
            scenario=scenario,
            session_id=session_id,
            responses=scored,
            consensus=analysis.get("consensus", []),
            dissent=analysis.get("dissent", []),
            ambiguity_analysis=analysis.get("ambiguity_analysis", []),
            risk_appetite_distribution=risk_dist,
            top_recommendation=analysis.get("top_recommendation", ""),
            metadata={
                "scenario_path": str(scenario_path) if scenario_path else "custom",
                "providers_used": list({m.provider for m in active_members}),
                "total_latency_seconds": round(total_latency, 1),
                "concurrent": self.config.session.concurrent,
            },
        )

        console.print(f"\n[green]Session complete.[/green] Total latency: {total_latency:.1f}s\n")
        return report

    # ─── Member resolution ────────────────────────────────────────────────────

    def _resolve_members(self, override: list[str] | None) -> list[MemberConfig]:
        """Determine which council members participate in this session.

        Filters out members whose provider has no API key configured.

        Args:
            override: If provided, only include these persona IDs.

        Returns:
            List of active MemberConfig objects.
        """
        candidates = [m for m in self.config.council_members if m.enabled]

        if override:
            candidates = [m for m in candidates if m.persona in override]
            # If override contains IDs not in config, add them with defaults.
            config_ids = {m.persona for m in candidates}
            for pid in override:
                if pid not in config_ids and pid in PERSONAS:
                    # Find a provider with a key; fall back to google.
                    for provider in ("google", "groq", "mistral", "openai"):
                        if get_api_key(provider):
                            candidates.append(
                                MemberConfig(
                                    persona=pid,
                                    provider=provider,
                                    model=_default_model(provider),
                                    enabled=True,
                                )
                            )
                            break

        # Filter to members whose provider key is available.
        active = []
        for m in candidates:
            if get_api_key(m.provider):
                active.append(m)
            else:
                console.print(
                    f"[dim yellow]Skipping {m.persona} ({m.provider}): "
                    f"no API key found.[/dim yellow]"
                )
        return active

    # ─── Response collection ─────────────────────────────────────────────────

    async def _collect_sequential(
        self,
        scenario: Scenario,
        members: list[MemberConfig],
    ) -> list[CouncilResponse]:
        """Collect responses one at a time (default mode for free tier safety)."""
        responses: list[CouncilResponse] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            for member in members:
                persona = get_persona(member.persona)
                task = progress.add_task(
                    f"[cyan]{persona.name}[/cyan] ({member.provider}/{member.model})...",
                    total=None,
                )
                response = await self._call_member(scenario, member, persona)
                progress.remove_task(task)
                status = "[red]error[/red]" if response.error else "[green]done[/green]"
                console.print(
                    f"  {persona.name} [{persona.title}] {status} "
                    f"({response.latency_seconds:.1f}s)"
                )
                responses.append(response)
        return responses

    async def _collect_concurrent(
        self,
        scenario: Scenario,
        members: list[MemberConfig],
    ) -> list[CouncilResponse]:
        """Collect all responses concurrently (only when rate limits allow)."""
        console.print("[dim]Running concurrently...[/dim]")
        tasks = [
            self._call_member(scenario, m, get_persona(m.persona))
            for m in members
        ]
        return list(await asyncio.gather(*tasks))

    async def _call_member(
        self,
        scenario: Scenario,
        member: MemberConfig,
        persona: Persona,
    ) -> CouncilResponse:
        """Make a single LLM call for one council member.

        Catches all exceptions and records them in the CouncilResponse.error
        field so the session can continue without this member.

        Args:
            scenario: The scenario to debate.
            member: The member's config (provider, model).
            persona: The persona definition.

        Returns:
            A CouncilResponse, possibly with error set.
        """
        api_key = get_api_key(member.provider) or ""
        system_prompt = build_persona_system_prompt(persona)
        user_prompt = build_scenario_user_prompt(scenario)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        start = time.monotonic()
        try:
            text = await get_completion(
                provider=member.provider,
                model=member.model,
                messages=messages,
                api_key=api_key,
                timeout=self.config.session.timeout,
            )
            latency = time.monotonic() - start
            return CouncilResponse(
                persona_id=persona.id,
                persona_title=persona.title,
                persona_name=persona.name,
                provider=member.provider,
                model=member.model,
                response_text=text,
                latency_seconds=round(latency, 2),
            )
        except Exception as exc:
            latency = time.monotonic() - start
            error_msg = f"{type(exc).__name__}: {exc}"
            console.print(f"  [red]Error from {persona.name}:[/red] {error_msg}")
            return CouncilResponse(
                persona_id=persona.id,
                persona_title=persona.title,
                persona_name=persona.name,
                provider=member.provider,
                model=member.model,
                response_text="",
                latency_seconds=round(latency, 2),
                error=error_msg,
            )

    # ─── Scoring ─────────────────────────────────────────────────────────────

    async def _score_all(
        self,
        scenario: Scenario,
        members: list[MemberConfig],
        responses: list[CouncilResponse],
    ) -> list[ScoredResponse]:
        """Score each response with the configured scoring model.

        Args:
            scenario: The debated scenario.
            members: Active council members (parallel to responses list).
            responses: Raw responses from LLM calls.

        Returns:
            List of ScoredResponse objects.
        """
        scoring_provider = self.config.scoring.provider
        scoring_model = self.config.scoring.model
        api_key = get_api_key(scoring_provider) or ""

        scored: list[ScoredResponse] = []
        member_by_persona = {m.persona: m for m in members}

        console.print("[dim]Scoring responses...[/dim]")
        for response in responses:
            persona = get_persona(response.persona_id)
            result = await score_response(
                scenario=scenario,
                persona=persona,
                response=response,
                scoring_provider=scoring_provider,
                scoring_model=scoring_model,
                api_key=api_key,
            )
            scored.append(result)

        return scored

    # ─── Risk distribution ────────────────────────────────────────────────────

    def _risk_distribution(self, members: list[MemberConfig]) -> dict[str, int]:
        """Count council members by risk appetite category.

        Args:
            members: Active council members.

        Returns:
            Dict mapping appetite name to count.
        """
        dist: dict[str, int] = {
            "ultra_conservative": 0,
            "conservative": 0,
            "moderate": 0,
            "tolerant": 0,
            "aggressive": 0,
        }
        appetite_map = {
            1: "ultra_conservative",
            2: "conservative",
            3: "moderate",
            4: "tolerant",
            5: "aggressive",
        }
        for m in members:
            try:
                persona = get_persona(m.persona)
                key = appetite_map.get(persona.risk_appetite.value, "moderate")
                dist[key] = dist.get(key, 0) + 1
            except KeyError:
                continue
        return dist


def _default_model(provider: str) -> str:
    """Return a sensible default model for a provider when no config is set.

    Args:
        provider: Provider name.

    Returns:
        Default model identifier string.
    """
    defaults: dict[str, str] = {
        "google": "gemini-2.5-flash",
        "groq": "llama-3.3-70b-versatile",
        "mistral": "mistral-small-latest",
        "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
        "openai": "gpt-4o-mini",
        "deepseek": "deepseek-chat",
    }
    return defaults.get(provider, "")
