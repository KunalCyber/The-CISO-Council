# The CISO Council

**A virtual council of AI models that debate real cybersecurity dilemmas.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Inspired by [Karpathy's LLM Council](https://github.com/karpathy/llm-council). Built for security professionals who make decisions under ambiguity every day.

---

## The Problem

Security decisions are rarely black and white.

Should you notify the regulator now or wait for more information? When a vendor fails their SOC 2, do you terminate the contract or work with them? Your AI model has a measurable bias, but it outperforms the current system by 23%: do you deploy? Your red team found a critical path to production, but patching it requires a three-week freeze: what is your position to the board?

These are judgement calls. They depend on your risk appetite, your organisational context, your regulatory exposure, and what your board will tolerate. There is no single right answer, and the consequences of getting it wrong are real.

Most "AI for security" tools automate the easy parts: policy generation, control mapping, compliance checklists. The CISO Council tackles the hard part: **decision-making under ambiguity**.

## What It Does

The CISO Council assembles 6 large language models, each embodying a distinct security leadership persona, feeds them the same scenario, and produces a structured council report.

```
SCENARIO
  "Your vendor disclosed a breach. 40,000 customer records potentially
   exposed. You have 24 hours before regulatory notification is triggered..."
        │
        ├──→  Divya Sharma, CISO (Fintech Startup)         ← Claude / Gemini
        ├──→  Marcus Chen, DPO (Healthtech)                ← GPT-4o / Llama
        ├──→  Sarah Al-Rashid, CRO (Regulated Bank)        ← Gemini / Mistral
        ├──→  James Okafor, Head of Internal Audit         ← Claude / Mixtral
        ├──→  Elena Voronova, CISO (Enterprise SaaS)       ← Grok / Gemini
        └──→  Dr. Tomoko Nakamura, Head of AI Governance   ← o3 / Cerebras
                │
                ▼
        SCORING ENGINE (5 dimensions × 6 responses)
                │
                ▼
        COUNCIL REPORT
        ✓ Consensus positions
        ✗ Dissenting views
        △ Ambiguity analysis
        ◆ Chief Arbiter recommendation
        ↓ Exportable PDF
```

## Who This Is For

This tool is for anyone who makes security decisions:

- **CISOs and security leaders** pressure-testing decisions before the board does it for you
- **Risk managers** who need to see how different risk appetites frame the same problem
- **Security architects** stress-testing a design decision against multiple professional perspectives
- **Incident responders** thinking through response options under time pressure
- **Compliance and privacy teams** navigating regulatory ambiguity
- **Penetration testers and consultants** preparing findings and remediation recommendations
- **Security teams** looking to surface blind spots and challenge groupthink
- **Students and early-career practitioners** learning how experienced security leaders reason differently about the same problem

---

## What Makes the Personas Different

These are not tone adjustments. Each persona has structured attributes that shape its reasoning:

| Attribute | Effect |
|---|---|
| **Risk appetite** (1-5) | Shapes whether they default to caution or action |
| **Organisational context** | Sector, size, and maturity determine what is realistic |
| **Regulatory lens** | Which frameworks they instinctively reference |
| **Decision style** | Data-driven, compliance-first, cost-optimised, pragmatic |

A startup CISO with a risk appetite of 4 will reason differently about the same breach than a bank CRO with an appetite of 1. That difference is the point.

## How Responses Are Scored

Every response is evaluated by a separate scoring model on five dimensions:

| Dimension | What It Measures |
|---|---|
| **Regulatory Defensibility** | Would this hold up under regulatory scrutiny? |
| **Practicality** | Can this be implemented with realistic resources? |
| **Board-Readiness** | Could you present this to a board without caveats? |
| **Specificity** | Concrete actions or just "conduct a risk assessment"? |
| **Risk Quantification** | Does it frame risk in business terms? |

---

## Quickstart

### 1. Clone and Install

```bash
git clone https://github.com/kunalrk/the-ciso-council.git
cd the-ciso-council
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Configure Keys and Council

```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

Open `.env` and add your API keys. Open `config.yaml` to choose which models each persona uses. The defaults use free tiers only.

### 3. Launch the War Room

```bash
python -m council serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### 4. Or Run via CLI

```bash
python -m council --scenario scenarios/incident_response/vendor_breach.yaml
```

---

## Model Configuration

### Recommended (Production)

Using frontier models produces significantly better council deliberations. Each member reasons more deeply, gives more specific recommendations, and the consensus/dissent analysis becomes genuinely useful for real decision-making.

| Council Seat | Provider | Model | Why |
|---|---|---|---|
| Divya Sharma (CISO) | Anthropic | claude-opus-4-5 | Deepest reasoning, most nuanced analysis |
| Marcus Chen (DPO) | OpenAI | gpt-4o | Strong regulatory knowledge, structured output |
| Sarah Al-Rashid (CRO) | Google | gemini-2.5-pro | Excellent quantitative reasoning, large context |
| James Okafor (Auditor) | Anthropic | claude-sonnet-4-5 | Fast, high-quality, cost-effective |
| Elena Voronova (CISO) | xAI | grok-3 | Independent reasoning, contrarian perspectives |
| Dr. Nakamura (AI Gov) | OpenAI | o3 | Superior reasoning for complex governance questions |
| Scoring Model | Google | gemini-2.5-flash | Fast, accurate scoring at low cost |

To activate: get API keys for the providers above, add them to `.env`, then uncomment the production section in `config.yaml`.

### Free Tier (Getting Started)

Start here to test the platform. When you see the value, upgrade to production models.

| Council Seat | Provider | Model | Cost |
|---|---|---|---|
| Divya Sharma (CISO) | Google | gemini-2.5-flash | Free |
| Marcus Chen (DPO) | Groq | llama-3.3-70b | Free |
| Sarah Al-Rashid (CRO) | Mistral | mistral-small-latest | Free |
| James Okafor (Auditor) | Groq | mixtral-8x7b | Free |
| Elena Voronova (CISO) | Google | gemini-2.5-flash-lite | Free |
| Dr. Nakamura (AI Gov) | Cerebras | llama3.1-8b | Free |
| Scoring Model | Google | gemini-2.5-flash | Free |

> You do not need all providers. The council runs with as few as two. Start with Google (easiest free tier) and add others as needed.

### Supported Providers

| Provider | Env Var | Notes |
|---|---|---|
| Google Gemini | `GOOGLE_API_KEY` | Free tier, also default scoring model |
| Anthropic | `ANTHROPIC_API_KEY` | Claude Opus, Sonnet, Haiku |
| OpenAI | `OPENAI_API_KEY` | GPT-4o, o3 |
| xAI | `XAI_API_KEY` | Grok-3 |
| Groq | `GROQ_API_KEY` | Fast Llama/Mixtral inference |
| Mistral | `MISTRAL_API_KEY` | 1B tokens/month free |
| OpenRouter | `OPENROUTER_API_KEY` | 24+ free models via one key |
| DeepSeek | `DEEPSEEK_API_KEY` | Strong reasoning |
| Cerebras | `CEREBRAS_API_KEY` | Fast Llama inference |

---

## Available Scenarios

### Incident Response
- **Vendor Breach** — Third-party breach with 40,000 customer records exposed, 72-hour notification clock running

### Risk Acceptance
- **Cloud Migration** — Accepting residual risk in an accelerated migration with 14 open high-severity findings

### AI Governance
- **Biased Lending Model** — Deploying an AI credit scoring model with known demographic bias under EU AI Act scrutiny

*More scenarios across vulnerability disclosure, ransomware response, insider threat, and board reporting are in development. Contributions welcome.*

---

## CLI Reference

```bash
# Run a specific scenario
python -m council --scenario <path_to_yaml>

# Run with specific council members only
python -m council --scenario <path> --members ciso_fintech_startup,dpo_healthtech

# Validate all scenario files
python -m council validate

# List available personas
python -m council personas

# List available scenarios
python -m council scenarios
```

---

## Project Structure

```
the-ciso-council/
├── council/
│   ├── __init__.py
│   ├── __main__.py       # Module entry point
│   ├── cli.py            # CLI interface
│   ├── config.py         # Configuration loader
│   ├── models.py         # Pydantic data models
│   ├── personas.py       # Council member definitions
│   ├── pdf_report.py     # PDF export engine
│   ├── prompts.py        # System prompts and scoring rubrics
│   ├── providers.py      # LLM provider abstraction
│   ├── report.py         # Report generator and consensus analysis
│   ├── scenarios.py      # Scenario loader and validator
│   ├── scoring.py        # Multi-dimensional scoring engine
│   ├── server.py         # FastAPI server (War Room UI)
│   └── session.py        # Council session orchestrator
├── scenarios/
│   ├── incident_response/
│   ├── risk_acceptance/
│   ├── ai_governance/
│   └── ...
├── static/               # War Room web UI
├── outputs/              # Generated reports (gitignored)
├── tests/
├── .env.example          # API key template
└── config.yaml.example   # Council config template
```

---

## Security

All API keys stay local. Nothing is logged, transmitted, or exported.

- Keys live in `.env` only (gitignored, never committed)
- The provider layer sanitises all error messages to remove key patterns before logging
- Output files (including PDFs) contain scenario text and model responses only, never credentials
- The server runs on localhost only and includes CORS restrictions
- No telemetry, no analytics, no data collection of any kind
- The `.gitignore` blocks all sensitive files, output reports, and the `.claude/` directory

If you accidentally expose a key, regenerate it immediately at the provider's console.

See [.github/SECURITY.md](.github/SECURITY.md) for the full security policy.

---

## Contributing

Contributions are welcome, particularly:

- **New scenarios** — Real-world security dilemmas across any domain. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **New personas** — Different sectors, regions, or leadership roles.
- **Provider integrations** — Additional LLM providers.
- **Scoring improvements** — Better rubrics or evaluation methods.

---

## How It Was Built

This project was built using [Claude Code](https://claude.ai/code), Anthropic's terminal-based coding agent. The `CLAUDE.md` file provides project context that makes Claude Code sessions productive from the first prompt.

```bash
cd the-ciso-council
claude
```

---

**Built by [Kunal RK](https://www.linkedin.com/in/kunal-rk-a255aa301/)**
