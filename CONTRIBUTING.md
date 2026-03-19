# Contributing to The CISO Council

Thank you for your interest in contributing. This project thrives on real-world security expertise, so practitioner contributions are especially valued.

## What We Need Most

### New Scenarios

The scenario bank is the heart of this project. Good scenarios are:
- Based on real-world security dilemmas (anonymised as needed)
- Specific enough to force a real decision, not just a discussion
- Genuinely ambiguous: reasonable security professionals should disagree
- Complete: context, constraints, stakeholders, and expected dimensions
- Relevant to the broad security community: CISOs, architects, incident responders, compliance teams, consultants

Scenarios should appeal to anyone making security decisions, not only compliance teams. Think: breach response, architecture trade-offs, vulnerability disclosure timing, ransomware negotiation, insider threat response, vendor risk acceptance, AI system governance, board communication under pressure.

See `scenarios/incident_response/vendor_breach.yaml` for the format.

### New Personas

Additional council members from different contexts:
- Different sectors: government, energy, retail, education, defence, critical infrastructure
- Different regions: APAC-focused, MENA-focused, LatAm-focused regulatory lenses
- Different roles: security architect, incident response lead, CISO of a regulated utility, vCISO

### Provider Integrations

Additional LLM providers that expand the council's reasoning diversity.

## Ground Rules

1. **No API keys or secrets in any PR.** Ever. For any reason. PRs containing credentials will be rejected immediately.
2. **British English spelling** in all user-facing text, comments, and documentation.
3. **No em dashes.** Use commas, colons, or restructure the sentence.
4. **No generic content.** Every scenario must be specific and realistic. "Implement best practices" is not a dilemma.
5. **Broad security framing.** Scenarios and personas should serve the whole security community, not only GRC/compliance functions.
6. **Type hints** on all function signatures. Docstrings on all public functions.
7. **Tests** for any new functionality. Mock providers are available in `tests/conftest.py`.

## Submitting a PR

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/scenario-ransomware-response`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Check no sensitive files are staged: `git diff --cached --name-only`
6. Submit a PR with a clear description of what you added and why

## Scenario YAML Format

```yaml
title: "Short, descriptive title"
domain: incident_response  # or risk_acceptance, vendor_risk, ai_governance, etc.

context: |
  2-4 sentences of background. Set the scene specifically.
  Include enough operational detail that the dilemma feels real.
  Avoid generic language — name specific numbers, timeframes, and constraints.

dilemma: |
  The specific question or decision the council must address.
  This should force a position. Reasonable professionals should disagree.
  Avoid open-ended discussion prompts — make it a decision.

constraints:
  - "Real operational constraint that limits options (specific, not generic)"
  - "Another constraint with concrete details"

stakeholders:
  - "Who is affected and how"
  - "Who has decision authority"
  - "Who will scrutinise the decision"

expected_dimensions:
  - "What a strong answer should address"
  - "Another dimension a practitioner would consider"
```

## Questions?

Open an issue or reach out on [LinkedIn](https://www.linkedin.com/in/kunal-rk-a255aa301/).
