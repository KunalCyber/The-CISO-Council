# CLAUDE.md — The CISO Council

## What This Project Is

The CISO Council is an open-source Python tool that assembles a virtual council of LLMs, each assigned a distinct security leadership persona, to debate real-world cybersecurity dilemmas. Inspired by Karpathy's LLM Council.

This is a tool for the entire information security community: CISOs, security architects, incident responders, risk managers, compliance teams, penetration testers, consultants, anyone who makes security decisions under ambiguity. It is not narrowly a GRC tool.

Each council member receives the same scenario, deliberates from their persona's perspective, and the system scores responses on security-relevant dimensions, identifies consensus, surfaces dissent, and generates a structured council report with PDF export.

**Author:** Kunal RK

## Architecture

```
council/
  __init__.py     — Package init
  models.py       — Pydantic data models (Persona, Scenario, Response, Score, Report)
  personas.py     — Persona definitions with risk appetite, org context, regulatory lens
  providers.py    — LLM provider abstraction (Anthropic, Google, OpenAI-compatible, xAI)
  scenarios.py    — Scenario loader and YAML validator
  session.py      — Orchestrates a council session (prompt > collect > score > report)
  scoring.py      — Multi-dimensional scoring engine (separate LLM call, json_mode)
  report.py       — Consensus/dissent report generator (Markdown + JSON)
  pdf_report.py   — Board-ready PDF export via ReportLab
  config.py       — Configuration loader (YAML + env vars via python-dotenv)
  cli.py          — CLI entry point using click
  server.py       — FastAPI server (War Room UI), localhost-only with CORS
  prompts.py      — System prompt templates for personas and scoring

scenarios/         — YAML scenario files organised by domain
static/            — War Room web UI (index.html)
outputs/           — Generated reports (gitignored except .gitkeep)
tests/             — pytest tests with mock providers
docs/              — Write-up and companion content
```

## Key Design Decisions

1. **Provider abstraction**: Groq, Mistral, OpenRouter, DeepSeek, Cerebras, xAI, and OpenAI all use the `openai` Python SDK with different `base_url` values. Anthropic uses its own SDK (`anthropic`). Google Gemini uses `google-genai`. All normalised to a single `get_completion(provider, model, messages)` interface with optional `temperature` and `json_mode` parameters.

2. **Two configuration tiers**: Free-tier setup (Gemini, Groq, Mistral, Cerebras) for getting started. Production setup (Claude, GPT-4o, Gemini Pro, Grok, o3) for serious decision support. Config documented in `config.yaml.example`.

3. **Personas are structured, not just tone**: Each persona has `risk_appetite` (1-5), `org_context` (sector, size, maturity), `regulatory_lens` (list of frameworks), and `decision_style`. These are injected into the system prompt via a template in `prompts.py`.

4. **Scoring uses json_mode and temperature=0**: The scoring LLM call uses `json_mode=True` (forces `response_mime_type: application/json` on Gemini, `response_format: json_object` on OpenAI-compatible) and `temperature=0.0` for deterministic, well-structured scores. Fallback scores are 0.0 (not 5.0) so failures are visible.

5. **Scenarios are YAML files**: Fields: `title`, `domain`, `context`, `dilemma`, `constraints`, `stakeholders`, `expected_dimensions`. Validated on load via Pydantic. Scenarios should appeal to the whole security community, not only compliance teams.

6. **Security hardening**: All error messages run through `sanitise_error()` in `providers.py` before logging or raising. This redacts known API key patterns. The server is localhost-only with CORS restrictions. `config.py` logs key status on startup without printing values. Fallback scores are 0.0 not 5.0.

7. **PDF export**: `pdf_report.py` uses ReportLab Platypus to produce board-ready A4 PDFs. Custom `_FooterCanvas` draws the footer on all pages except the cover. Served from `/api/session/latest/export` as a file download.

## Code Conventions

- Python 3.10+ with type hints on all function signatures
- Docstrings (Google style) on all public functions and classes
- British English in all user-facing text, docstrings, and comments
- No em dashes anywhere (use commas, colons, or rewrite)
- f-strings preferred over `.format()`
- asyncio for all LLM calls (sequential by default, concurrent optional)
- Pydantic v2 for all data models
- rich for terminal output, progress bars, and tables
- tenacity for retry logic with exponential backoff

## Dependencies

```
openai>=1.0
google-genai>=1.0
anthropic>=0.34
pydantic>=2.0
pyyaml>=6.0
python-dotenv>=1.0
rich>=13.0
tenacity>=8.0
click>=8.0
fastapi>=0.109
uvicorn[standard]>=0.27
reportlab>=4.0
pytest>=7.0
pytest-asyncio>=0.21
```

## Commands

```bash
# Launch the War Room UI
python -m council serve

# Run a council session on a specific scenario (CLI)
python -m council --scenario scenarios/incident_response/vendor_breach.yaml

# Run with specific council members only
python -m council --scenario <path> --members ciso_fintech_startup,dpo_healthtech

# Validate all scenario YAML files
python -m council validate

# List available personas
python -m council personas

# List available scenarios
python -m council scenarios
```

## Testing

```bash
pytest tests/ -v
pytest tests/ -k "test_scoring" -v
```

Mock providers are available in `tests/conftest.py` for testing without API keys.

## What Good Looks Like

- A council session completes in under 3 minutes with sequential calls on free tiers
- Scoring returns real scores (not all 5s): check server console for `[SCORING]` log lines after a session
- Persona responses feel genuinely different, not just the same answer with different adjectives
- Scoring is defensible: if you read the rubric and the response, the score makes sense
- Error handling is graceful: if one provider is down, the session continues with the rest
- PDF export produces a clean, professional document suitable for sharing

## What to Avoid

- Generic placeholder text in scenarios (every scenario must be a real, specific security dilemma)
- Hardcoded API keys or provider URLs anywhere in code
- Printing raw error messages without running through `sanitise_error()` first
- Narrowing the tool to GRC/compliance: scenarios and language should serve the whole security community
- Circular imports between council modules
- Amending the `.gitignore` in ways that could allow sensitive files to be committed
