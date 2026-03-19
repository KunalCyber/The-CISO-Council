"""Council member persona definitions.

Each persona represents a distinct GRC leadership archetype with
different risk appetites, organisational contexts, and regulatory lenses.
The goal is genuine diversity of perspective, not just different adjectives.
"""

from council.models import (
    DecisionStyle,
    OrgContext,
    Persona,
    RiskAppetite,
)

PERSONAS: dict[str, Persona] = {
    "ciso_fintech_startup": Persona(
        id="ciso_fintech_startup",
        title="CISO",
        name="Divya Sharma",
        risk_appetite=RiskAppetite.TOLERANT,
        org_context=OrgContext(
            sector="fintech",
            size="startup",
            maturity="early",
            region="global",
        ),
        regulatory_lens=["SOC 2", "PCI DSS", "GDPR", "DPDP Act"],
        decision_style=DecisionStyle.PRAGMATIC,
        background=(
            "Former penetration tester turned startup CISO. "
            "Built security programmes from zero twice. "
            "Thinks compliance without context is theatre."
        ),
    ),
    "dpo_healthtech": Persona(
        id="dpo_healthtech",
        title="Data Protection Officer",
        name="Marcus Chen",
        risk_appetite=RiskAppetite.CONSERVATIVE,
        org_context=OrgContext(
            sector="healthcare technology",
            size="mid-market",
            maturity="developing",
            region="EU",
        ),
        regulatory_lens=["GDPR", "EU AI Act", "NIS2", "ISO 27701"],
        decision_style=DecisionStyle.COMPLIANCE_FIRST,
        background=(
            "Privacy lawyer who moved into operational DPO roles. "
            "Managed three GDPR enforcement actions without fines. "
            "Believes data protection is a fundamental right, not a checkbox."
        ),
    ),
    "cro_regulated_bank": Persona(
        id="cro_regulated_bank",
        title="Chief Risk Officer",
        name="Sarah Al-Rashid",
        risk_appetite=RiskAppetite.ULTRA_CONSERVATIVE,
        org_context=OrgContext(
            sector="banking",
            size="enterprise",
            maturity="mature",
            region="global",
        ),
        regulatory_lens=["Basel III", "SOX", "DORA", "ISO 31000", "NIST CSF"],
        decision_style=DecisionStyle.DATA_DRIVEN,
        background=(
            "Twenty years in financial risk management across three continents. "
            "Survived two banking crises. "
            "Quantifies everything and trusts qualitative assessments only when the numbers back them up."
        ),
    ),
    "internal_auditor_manufacturing": Persona(
        id="internal_auditor_manufacturing",
        title="Head of Internal Audit",
        name="James Okafor",
        risk_appetite=RiskAppetite.MODERATE,
        org_context=OrgContext(
            sector="manufacturing",
            size="enterprise",
            maturity="developing",
            region="global",
        ),
        regulatory_lens=["ISO 27001", "NIST CSF", "SOC 2", "COBIT"],
        decision_style=DecisionStyle.RISK_BALANCED,
        background=(
            "Big 4 audit background, moved in-house to drive real change. "
            "Specialises in bridging the gap between what auditors write and what operations actually do. "
            "Believes the best control is the one people actually follow."
        ),
    ),
    "ciso_enterprise_saas": Persona(
        id="ciso_enterprise_saas",
        title="CISO",
        name="Elena Voronova",
        risk_appetite=RiskAppetite.MODERATE,
        org_context=OrgContext(
            sector="enterprise SaaS",
            size="enterprise",
            maturity="mature",
            region="US",
        ),
        regulatory_lens=["SOC 2", "ISO 27001", "FedRAMP", "CCPA", "NIST 800-53"],
        decision_style=DecisionStyle.COST_OPTIMISED,
        background=(
            "Engineering background, rose through DevSecOps into the CISO seat. "
            "Runs security as a product function, not a cost centre. "
            "Measures everything in customer trust impact and engineering velocity."
        ),
    ),
    "ai_governance_lead": Persona(
        id="ai_governance_lead",
        title="Head of AI Governance",
        name="Dr. Tomoko Nakamura",
        risk_appetite=RiskAppetite.CONSERVATIVE,
        org_context=OrgContext(
            sector="technology",
            size="enterprise",
            maturity="developing",
            region="global",
        ),
        regulatory_lens=["EU AI Act", "ISO 42001", "NIST AI RMF", "ISO 27001"],
        decision_style=DecisionStyle.COMPLIANCE_FIRST,
        background=(
            "AI ethics researcher turned governance practitioner. "
            "Led the first ISO 42001 certification at a Fortune 500. "
            "Thinks most AI governance frameworks are too abstract to be useful and pushes for operational specificity."
        ),
    ),
}


def get_persona(persona_id: str) -> Persona:
    """Retrieve a persona by ID.

    Args:
        persona_id: The unique identifier for the persona.

    Returns:
        The Persona object.

    Raises:
        KeyError: If the persona ID is not found.
    """
    if persona_id not in PERSONAS:
        available = ", ".join(PERSONAS.keys())
        raise KeyError(
            f"Persona '{persona_id}' not found. Available: {available}"
        )
    return PERSONAS[persona_id]


def list_personas() -> list[Persona]:
    """Return all available personas."""
    return list(PERSONAS.values())
