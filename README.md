<p align="center">
  <img src="https://github.com/KunalCyber/The-CISO-Council/blob/main/docs/screenshots/landing-page.png?raw=true" alt="The CISO Council" width="800">
</p>

<h1 align="center">The CISO Council</h1>

<p align="center">
  <strong>Can't afford a 7-figure CISO? Assemble a 6-member AI security council instead.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Cost-%240-brightgreen?style=for-the-badge" alt="Zero Cost">
  <img src="https://img.shields.io/badge/AI%20Models-6-7c3aed?style=for-the-badge" alt="6 Models">
  <a href="https://github.com/karpathy/llm-council"><img src="https://img.shields.io/badge/Inspired%20by-Karpathy's%20LLM%20Council-orange?style=for-the-badge" alt="Inspired by Karpathy"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#the-council">The Council</a> &bull;
  <a href="#recommended-models">Models</a> &bull;
  <a href="#security">Security</a> &bull;
  <a href="https://www.linkedin.com/in/kunal-rk-a255aa301">LinkedIn</a>
</p>

---

## How It Works

Instead of asking a security question to your favourite LLM, you assemble a **council of six AI models**, each embodying a distinct cybersecurity leadership persona with their own risk appetite, organisational context, and regulatory lens. Your query goes to all six independently, a scoring engine evaluates each response across five dimensions, and a **Chief Arbiter** synthesises the final verdict.

**Stage 1: Independent Deliberation.** Your cybersecurity dilemma is given to all 6 council members individually. Each responds from their persona's perspective: a startup CISO reasons differently from a bank CRO, a DPO prioritises differently from a Head of Internal Audit.

**Stage 2: Multi-Dimensional Scoring.** Each response is scored by a separate model across five dimensions: Regulatory Defensibility, Practicality, Board-Readiness, Specificity, and Risk Quantification. No self-grading: the scoring model is independent of the council members.

**Stage 3: Consensus and Dissent.** The Chief Arbiter analyses all scored responses and identifies where the council agrees, where they split, and what those disagreements reveal about the decision's inherent ambiguity.

**Stage 4: Board-Ready Report.** Export a clean PDF report with the full council deliberation, individual scores, consensus positions, dissenting views, and the Chief Arbiter's recommendation.

> **This is not a chatbot. It is a cybersecurity advisory board that runs on localhost.**

---

## The War Room

<p align="center">
  <img src="https://raw.githubusercontent.com/KunalCyber/The-CISO-Council/main/docs/screenshots/war-room.png" alt="The CISO Council War Room" width="900">
</p>

The CISO Council runs as a local web application with a dark, command-centre-style interface. Select a pre-built scenario or type your own cybersecurity dilemma, hit "Convene Council", and watch six AI security leaders deliberate in real time.

### Features

| Feature | Description |
|:---|:---|
| 🎭 **6 AI Personas** | Each with distinct risk appetite, org context, and regulatory lens |
| 🤖 **Multi-Model** | Uses different AI models from different providers for genuine diversity |
| 📊 **5-Dimension Scoring** | Regulatory Defensibility, Practicality, Board-Readiness, Specificity, Risk Quantification |
| ⚖️ **Chief Arbiter** | Independent model synthesises the final verdict from all responses |
| 🤝 **Consensus/Dissent** | Identifies where the council agrees and where they split |
| 🔍 **Ambiguity Analysis** | Reveals what disagreements tell you about the decision's complexity |
| ✍️ **Custom Scenarios** | Type any cybersecurity dilemma directly into the War Room |
| 📄 **PDF Export** | Board-ready report with full deliberation, scores, and recommendations |
| 💰 **Zero Cost** | Runs entirely on free-tier API keys |
| 🔒 **Fully Local** | Nothing leaves your machine except API calls to your configured providers |

---

## The Council

Six personas, each with a different risk appetite, organisational context, and decision-making style.

| | Name | Role | Sector | Risk Appetite | Regulatory Focus |
|:---:|:---|:---|:---|:---|:---|
| 🟣 | **Divya Sharma** | CISO | Fintech Startup | 🟥🟥🟥🟥⬜ Tolerant | SOC 2, PCI DSS, GDPR, DPDP |
| 🟢 | **Marcus Chen** | Data Protection Officer | Healthtech | 🟩🟩⬜⬜⬜ Conservative | GDPR, EU AI Act, NIS2, ISO 27701 |
| 🔵 | **Sarah Al-Rashid** | Chief Risk Officer | Banking | 🟩⬜⬜⬜⬜ Ultra-Conservative | Basel III, DORA, SOX, ISO 31000 |
| 🟡 | **James Okafor** | Head of Internal Audit | Manufacturing | 🟧🟧🟧⬜⬜ Moderate | ISO 27001, NIST CSF, SOC 2, COBIT |
| ⚪ | **Elena Voronova** | CISO | Enterprise SaaS | 🟧🟧🟧⬜⬜ Moderate | SOC 2, ISO 27001, FedRAMP, NIST 800-53 |
| 🔴 | **Dr. Tomoko Nakamura** | Head of AI Governance | Technology | 🟩🟩⬜⬜⬜ Conservative | EU AI Act, ISO 42001, NIST AI RMF |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/KunalCyber/The-CISO-Council.git
cd The-CISO-Council
```

### 2. Install

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Get Free API Keys

| Provider | Free Tier | Get Your Key |
|:---|:---|:---|
| 🔷 **Google AI Studio** | ~500 requests/day | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| ⚡ **Groq** | 14,400 requests/day | [console.groq.com/keys](https://console.groq.com/keys) |
| 🔶 **Mistral** | 1B tokens/month | [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys) |
| 🧠 **Cerebras** | Generous free tier | [cloud.cerebras.ai](https://cloud.cerebras.ai) |

> **You only need 2 providers minimum** to run a council session. Start with Google and Groq.

### 4. Configure

```bash
cp .env.example .env        # Add your API keys
cp config.yaml.example config.yaml
```

### 5. Launch the War Room

```bash
python -m council serve
```

Open **http://localhost:8000** in your browser. Select a scenario or type your own. Hit **"Convene Council"**.

---

## Recommended Models

### 🏢 Production Setup (Best Results)

For serious decision support, use frontier models. The quality of deliberation is dramatically better.

| Council Seat | Provider | Model | Why |
|:---|:---|:---|:---|
| Divya Sharma | Anthropic | `claude-opus-4` | Deepest reasoning, most nuanced analysis |
| Marcus Chen | OpenAI | `gpt-4o` | Strong regulatory knowledge, structured output |
| Sarah Al-Rashid | Google | `gemini-2.5-pro` | Excellent quantitative reasoning, large context |
| James Okafor | Anthropic | `claude-sonnet-4.6` | Fast, high-quality, cost-effective |
| Elena Voronova | xAI | `grok-3` | Independent reasoning, contrarian perspectives |
| Dr. Nakamura | OpenAI | `o3` | Superior reasoning for complex governance questions |
| **Scoring Model** | Anthropic | `claude-sonnet-4.6` | Best balance of reasoning depth and speed for evaluation |

> 💡 **The scoring model is the most important model choice.** It evaluates every council member's response and generates the consensus/dissent analysis. A stronger scoring model produces dramatically more accurate and useful verdicts.

### 🆓 Free Tier Setup (Getting Started)

Start here. Zero cost, works out of the box.

| Council Seat | Provider | Model | Cost |
|:---|:---|:---|:---|
| Divya Sharma | Google | `gemini-2.5-flash` | Free |
| Marcus Chen | Groq | `llama-3.3-70b-versatile` | Free |
| Sarah Al-Rashid | Mistral | `mistral-small-latest` | Free |
| James Okafor | Groq | `mixtral-8x7b-32768` | Free |
| Elena Voronova | Google | `gemini-2.5-flash-lite` | Free |
| Dr. Nakamura | Cerebras | `llama3.1-8b` | Free |
| **Scoring Model** | Google | `gemini-2.5-flash` | Free |

---

## Scoring Dimensions

Every council response is evaluated independently on five dimensions:

| Dimension | What It Measures | Score Range |
|:---|:---|:---:|
| 📋 **Regulatory Defensibility** | Would this position hold up under regulatory scrutiny? | 1-10 |
| 🔧 **Practicality** | Can this be implemented with realistic resources? | 1-10 |
| 🏛️ **Board-Readiness** | Could you present this to a board without caveats? | 1-10 |
| 🎯 **Specificity** | Concrete actions or just "conduct a risk assessment"? | 1-10 |
| 📈 **Risk Quantification** | Does it frame risk in business terms? | 1-10 |

---

## Built-in Scenarios

| Domain | Scenario | What It Tests |
|:---|:---|:---|
| 🚨 **Incident Response** | Third-party vendor breach with customer data exposure | Notification timing, vendor management, board communication |
| ⚖️ **Risk Acceptance** | Accepting residual risk in accelerated cloud migration | Risk thresholds, compensating controls, audit implications |
| 🤖 **AI Governance** | Deploying AI credit scoring model with known demographic bias | EU AI Act compliance, bias thresholds, phased deployment |

**Plus:** type any cybersecurity dilemma directly into the War Room's custom scenario input.

---

## Security

| Principle | Implementation |
|:---|:---|
| 🔑 **Keys stay local** | All API keys in `.env` only, never committed, never logged, never exported |
| 🏠 **Runs on localhost** | No public server, no external access |
| 📡 **No telemetry** | Zero analytics, zero data collection, zero tracking |
| 📄 **Clean exports** | PDF reports contain only scenario text and model responses, never credentials |
| 🛡️ **Sanitised errors** | API keys are redacted from all error messages and logs |
| 🚫 **Gitignored** | `.env`, `config.yaml`, `outputs/`, `.claude/` are all blocked from git |

---

## Project Structure

```
The-CISO-Council/
├── council/
│   ├── cli.py              # CLI with serve command
│   ├── config.py           # Configuration loader
│   ├── models.py           # Pydantic data models
│   ├── personas.py         # 6 council member definitions
│   ├── prompts.py          # System prompts and scoring rubrics
│   ├── providers.py        # Multi-provider LLM abstraction
│   ├── scoring.py          # 5-dimension scoring engine
│   ├── session.py          # Council session orchestrator
│   ├── report.py           # Report generator
│   ├── pdf_report.py       # Board-ready PDF export
│   └── server.py           # FastAPI server (War Room backend)
├── static/
│   ├── index.html          # War Room frontend
│   └── council-hero.png    # Landing page hero image
├── scenarios/              # YAML scenario bank
├── outputs/                # Generated reports (gitignored)
├── docs/                   # Write-up and documentation
├── .env.example            # API key template
├── config.yaml.example     # Council configuration template
├── requirements.txt
└── CLAUDE.md               # Project context for Claude Code
```

---

## Contributing

We welcome contributions, particularly new scenarios, new personas, and provider integrations. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Inspired By

[Andrej Karpathy's LLM Council](https://github.com/karpathy/llm-council) for the original concept of assembling multiple LLMs to deliberate on hard questions. The CISO Council takes that idea and builds it into a complete cybersecurity decision-support tool with personas, scoring, consensus analysis, and board-ready exports.

---

<p align="center">
  <img src="https://img.shields.io/badge/%E2%AD%90_Star_this_repo-if_it_helped_you_think_differently-7c3aed?style=for-the-badge" alt="Star this repo">
</p>

<p align="center">
  <a href="https://github.com/KunalCyber/The-CISO-Council/stargazers"><img src="https://img.shields.io/github/stars/KunalCyber/The-CISO-Council?style=social" alt="Stars"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://github.com/KunalCyber/The-CISO-Council/network/members"><img src="https://img.shields.io/github/forks/KunalCyber/The-CISO-Council?style=social" alt="Forks"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://github.com/KunalCyber/The-CISO-Council/watchers"><img src="https://img.shields.io/github/watchers/KunalCyber/The-CISO-Council?style=social" alt="Watchers"></a>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/kunal-rk-a255aa301"><img src="https://img.shields.io/badge/Connect_on-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/KunalCyber"><img src="https://img.shields.io/badge/Follow_on-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
</p>

<p align="center">
  <strong>Built by <a href="https://www.linkedin.com/in/kunal-rk-a255aa301">Kunal RK</a></strong>
  <br>
  <sub>Taking the hardest security decisions and making them a council vote.</sub>
</p>
