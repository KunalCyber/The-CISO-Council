"""Configuration loader for The CISO Council.

Loads config from two sources, in order:
1. .env (API keys via python-dotenv)
2. config.yaml (or config.yaml.example as fallback)

API keys are read from environment variables only, never from config.yaml.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"
_CONFIG_EXAMPLE_PATH = _PROJECT_ROOT / "config.yaml.example"

# Maps provider names to their environment variable names.
PROVIDER_ENV_VARS: dict[str, str] = {
    "google":     "GOOGLE_API_KEY",
    "anthropic":  "ANTHROPIC_API_KEY",
    "openai":     "OPENAI_API_KEY",
    "xai":        "XAI_API_KEY",
    "groq":       "GROQ_API_KEY",
    "mistral":    "MISTRAL_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "deepseek":   "DEEPSEEK_API_KEY",
    "cerebras":   "CEREBRAS_API_KEY",
}

# Placeholder patterns in .env.example — treat these as unset.
_PLACEHOLDER_MARKERS = ("your_", "_here", "placeholder")


class MemberConfig(BaseModel):
    """Configuration for a single council member."""

    persona: str = Field(description="Persona ID from personas.py")
    provider: str = Field(description="LLM provider name")
    model: str = Field(description="Model identifier for this provider")
    enabled: bool = True


class ScoringConfig(BaseModel):
    """Configuration for the scoring model."""

    provider: str = "google"
    model: str = "gemini-2.5-flash"
    dimensions: list[str] = Field(
        default_factory=lambda: [
            "regulatory_defensibility",
            "practicality",
            "board_readiness",
            "specificity",
            "risk_quantification",
        ]
    )


class RateLimitsConfig(BaseModel):
    """Requests-per-minute limits per provider (for free tier safety)."""

    google: int = 5
    groq: int = 20
    mistral: int = 5
    openrouter: int = 10
    openai: int = 3
    deepseek: int = 5


class OutputConfig(BaseModel):
    """Report output configuration."""

    format: str = "both"
    directory: str = "outputs"
    include_raw: bool = True
    include_scores: bool = True


class SessionConfig(BaseModel):
    """Session execution configuration."""

    timeout: int = 120
    retries: int = 3
    concurrent: bool = False


class Config(BaseModel):
    """Top-level configuration object for a council session."""

    council_members: list[MemberConfig] = Field(default_factory=list)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    rate_limits: RateLimitsConfig = Field(default_factory=RateLimitsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)


def load_config() -> Config:
    """Load configuration from .env and config.yaml.

    Falls back to config.yaml.example if config.yaml does not exist.
    Returns a Config with defaults if neither file is found.

    Returns:
        Fully populated Config object.
    """
    # Load .env first so os.environ is populated for get_api_key.
    if _ENV_PATH.exists():
        from dotenv import load_dotenv
        load_dotenv(_ENV_PATH, override=False)

    config_path = _CONFIG_PATH if _CONFIG_PATH.exists() else _CONFIG_EXAMPLE_PATH
    if not config_path.exists():
        return Config()

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Parse council members.
    members: list[MemberConfig] = []
    for m in data.get("council", {}).get("members", []):
        members.append(
            MemberConfig(
                persona=m["persona"],
                provider=m["provider"],
                model=m["model"],
                enabled=m.get("enabled", True),
            )
        )

    # Parse scoring.
    sd = data.get("scoring", {})
    scoring = ScoringConfig(
        provider=sd.get("provider", "google"),
        model=sd.get("model", "gemini-2.5-flash"),
        dimensions=sd.get("dimensions", ScoringConfig().dimensions),
    )

    # Parse rate limits.
    rl_data = data.get("rate_limits", {})
    rate_limits = RateLimitsConfig.model_validate(
        {k: v for k, v in rl_data.items() if k in RateLimitsConfig.model_fields}
    ) if rl_data else RateLimitsConfig()

    # Parse output.
    od = data.get("output", {})
    output = OutputConfig(
        format=od.get("format", "both"),
        directory=od.get("directory", "outputs"),
        include_raw=od.get("include_raw", True),
        include_scores=od.get("include_scores", True),
    )

    # Parse session.
    sess = data.get("session", {})
    session = SessionConfig(
        timeout=sess.get("timeout", 120),
        retries=sess.get("retries", 3),
        concurrent=sess.get("concurrent", False),
    )

    return Config(
        council_members=members,
        scoring=scoring,
        rate_limits=rate_limits,
        output=output,
        session=session,
    )


def get_api_key(provider: str) -> str | None:
    """Return the API key for a provider from environment variables.

    Returns None if the key is not set or is still an example placeholder.
    Never raises. Never logs the key value itself.

    Args:
        provider: Provider name (e.g. 'google', 'groq').

    Returns:
        The API key string, or None if unavailable.
    """
    env_var = PROVIDER_ENV_VARS.get(provider.lower())
    if not env_var:
        return None
    value = os.environ.get(env_var, "").strip()
    if not value:
        return None
    lower = value.lower()
    if any(marker in lower for marker in _PLACEHOLDER_MARKERS):
        return None
    return value


def log_key_status() -> None:
    """Print which provider keys are set and which are missing.

    Prints only 'set' or 'missing', never the key values themselves.
    """
    from rich.console import Console
    c = Console()
    c.print("\n[dim]API key status:[/dim]")
    for provider, env_var in PROVIDER_ENV_VARS.items():
        value = os.environ.get(env_var, "").strip()
        lower = value.lower()
        is_placeholder = any(marker in lower for marker in _PLACEHOLDER_MARKERS)
        if value and not is_placeholder:
            c.print(f"  [green]{env_var}: set[/green]")
        else:
            c.print(f"  [dim]{env_var}: missing[/dim]")
