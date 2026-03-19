# Security Policy

## Responsible Disclosure

If you discover a security vulnerability in The CISO Council, please report it responsibly.

Open a GitHub issue with the label `security`. Do not disclose vulnerabilities publicly until they have been addressed.

For sensitive disclosures, reach out directly via [LinkedIn](https://www.linkedin.com/in/kunal-rk-a255aa301/).

## What This Tool Processes

The CISO Council processes:
- Scenario text you provide (either pre-built YAML files or custom input)
- Model responses from the LLM providers you configure
- Scoring output from your configured scoring model

It does not process personal data, credentials, or anything beyond what you explicitly submit as a scenario.

**This tool runs locally on your machine.** No data is sent anywhere except to the LLM providers you configure in `.env`. Your scenarios and responses go directly to those providers' APIs. The CISO Council itself does not collect, store, or transmit any data.

## API Key Safety

API keys are stored only in your local `.env` file and are:
- Never logged to the console (the provider layer sanitises all error messages)
- Never included in PDF or Markdown exports
- Never transmitted anywhere except directly to the provider API
- Never committed to the repository (`.env` is gitignored)

If you accidentally commit a key, rotate it immediately at the provider's console. Git history can be scrubbed with `git filter-branch` or `git filter-repo`, but rotating the key is faster and more reliable.

## Security Design Principles

### API Key Protection
- All keys are loaded from environment variables via `.env`
- `.env` is gitignored; only `.env.example` (with placeholder values) is committed
- The provider abstraction layer runs all error messages through `sanitise_error()` before logging or raising
- `sanitise_error()` redacts known key patterns: `sk-`, `sk-ant-`, `gsk_`, `xai-`, `AIza`, `nvapi-`

### Output Safety
- PDF and Markdown exports contain scenario text and model responses only
- No API keys, configuration details, or provider credentials appear in any export
- Output files are gitignored by default

### Local-Only Operation
- The FastAPI server binds to localhost and enforces CORS restrictions
- It is not designed for public deployment without additional authentication
- There is no telemetry, analytics, or phone-home functionality of any kind

### For Contributors
- Never hardcode API keys, tokens, or secrets in source code
- Never log or print key values, even in debug mode
- Never include real keys in test fixtures (use mock providers from `tests/conftest.py`)
- Always use `sanitise_error()` when constructing exception messages in the provider layer
- Review `.gitignore` before committing to confirm no sensitive files are staged

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
