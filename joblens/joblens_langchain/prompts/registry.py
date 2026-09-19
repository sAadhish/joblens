# ===================================
# PROMPT REGISTRY
# Version-controlled prompt templates.
# Change a prompt → bump the version → old behavior traceable.
# ===================================

PROMPTS = {
    "classify_v1": {
        "version": "1.0",
        "template": """
Classify: {question}
Types: jd|resume|comparison|general
If jd, extract company name.
Reply ONLY:
CATEGORY: <type>
COMPANY: <name or none>
""",
        "description": "Compact classification prompt"
    },

    "generate_v1": {
        "version": "1.0",
        "template": """
You are a career advisor for tech professionals in India.
Answer using ONLY the provided documents.
If answer not in documents: "I don't have enough information to answer that."
Cite sources like [Source 1: Company JD].

DOCUMENTS:
{context}
""",
        "description": "Grounded generation with citation"
    },

    "reformulate_v1": {
        "version": "1.0",
        "template": """
Rewrite as keyword-dense search query.
Original: {question}
Attempt: {iteration}
Return ONLY the rewritten query.
""",
        "description": "Query reformulation for retry"
    }
}


def get_prompt(name: str) -> dict:
    """Get a prompt by name. Raises KeyError if not found."""
    if name not in PROMPTS:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(PROMPTS.keys())}")
    return PROMPTS[name]


def get_template(name: str) -> str:
    """Get just the template string."""
    return get_prompt(name)["template"]


def list_prompts() -> list:
    """List all registered prompts with versions."""
    return [
        {"name": k, "version": v["version"], "description": v["description"]}
        for k, v in PROMPTS.items()
    ]