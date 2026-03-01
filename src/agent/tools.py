"""
Agent tools for future expansion.

Currently the agent operates purely via the system prompt knowledge base.
Tools can be added here for dynamic lookups (e.g., real-time pricing,
appointment availability, CRM integration).
"""

PRICING_TABLE = {
    "starter": {
        "name": "Starter",
        "price": 497,
        "agents": 2,
        "features": [
            "Até 2 agentes à escolha",
            "Integrações básicas (WhatsApp, planilhas)",
            "Suporte por e-mail",
            "Relatórios mensais",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 1297,
        "agents": 5,
        "features": [
            "Até 5 agentes à escolha",
            "Integrações avançadas (ERPs, APIs, TISS)",
            "Dashboard BI integrado",
            "Suporte prioritário",
            "Relatórios semanais",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": None,
        "agents": 7,
        "features": [
            "Todos os 7 agentes",
            "Personalização sob demanda",
            "SLA dedicado",
            "Integrações ilimitadas",
            "Gerente de conta exclusivo",
            "Treinamento da equipe",
        ],
    },
}

COOPERATIVE_DISCOUNTS = {
    "2-3": 0.15,
    "4-6": 0.25,
    "7-10": 0.35,
}

SPECIALTIES = [
    "Clínica Médica",
    "Odontologia",
    "Psicologia",
    "Estética e Dermatologia",
    "Fisioterapia",
    "Nutrição",
    "Fonoaudiologia",
    "Oftalmologia",
    "Ortopedia",
    "Pediatria",
    "Ginecologia e Obstetrícia",
    "Cardiologia",
    "Multiprofissional",
    "Terapias Complementares",
]


def get_pricing(plan: str) -> dict | None:
    return PRICING_TABLE.get(plan.lower())


def get_cooperative_discount(members: int) -> float:
    if 2 <= members <= 3:
        return COOPERATIVE_DISCOUNTS["2-3"]
    elif 4 <= members <= 6:
        return COOPERATIVE_DISCOUNTS["4-6"]
    elif 7 <= members <= 10:
        return COOPERATIVE_DISCOUNTS["7-10"]
    return 0.0


def is_supported_specialty(specialty: str) -> bool:
    return any(
        specialty.lower() in s.lower()
        for s in SPECIALTIES
    )
