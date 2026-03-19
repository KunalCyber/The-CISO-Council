"""Scenario loader and validator for The CISO Council.

Scenarios are YAML files under the scenarios/ directory.
Each file is validated against the Scenario pydantic model on load.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from council.models import Scenario

_PROJECT_ROOT = Path(__file__).parent.parent
_SCENARIOS_DIR = _PROJECT_ROOT / "scenarios"


def load_scenario(path: str | Path) -> Scenario:
    """Load and validate a scenario from a YAML file.

    Args:
        path: Path to the scenario YAML file. May be absolute or relative
            to the project root.

    Returns:
        A validated Scenario object.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is invalid or fails pydantic validation.
    """
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _PROJECT_ROOT / resolved

    if not resolved.exists():
        raise FileNotFoundError(f"Scenario file not found: {resolved}")

    with open(resolved, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Scenario file must be a YAML mapping: {resolved}")

    try:
        return Scenario.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Scenario validation failed for '{resolved.name}': {exc}") from exc


def list_scenarios(scenarios_dir: Path | None = None) -> list[dict]:
    """List all available scenario YAML files.

    Args:
        scenarios_dir: Directory to search. Defaults to scenarios/ in project root.

    Returns:
        List of dicts with keys: path (relative to project root), title, domain.
    """
    search_dir = scenarios_dir or _SCENARIOS_DIR
    results: list[dict] = []

    for yaml_path in sorted(search_dir.rglob("*.yaml")):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            rel_path = str(yaml_path.relative_to(_PROJECT_ROOT))
            results.append(
                {
                    "path": rel_path,
                    "title": data.get("title", yaml_path.stem),
                    "domain": data.get("domain", "unknown"),
                }
            )
        except Exception:
            continue

    return results


def validate_all(scenarios_dir: Path | None = None) -> list[dict]:
    """Validate all scenario YAML files in a directory.

    Args:
        scenarios_dir: Directory to search. Defaults to scenarios/ in project root.

    Returns:
        List of dicts with keys: path, status ('ok' or 'error'), message.
    """
    search_dir = scenarios_dir or _SCENARIOS_DIR
    results: list[dict] = []

    for yaml_path in sorted(search_dir.rglob("*.yaml")):
        try:
            load_scenario(yaml_path)
            results.append({"path": str(yaml_path), "status": "ok", "message": ""})
        except Exception as exc:
            results.append(
                {"path": str(yaml_path), "status": "error", "message": str(exc)}
            )

    return results
