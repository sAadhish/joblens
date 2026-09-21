"""
Prompt version registry.
Returns the currently deployed prompt versions for observability.
"""


def list_prompts() -> dict:
    """List all prompt versions currently deployed."""
    return {
        "rag_prompt": {
            "version": "1.0",
            "description": "Career advisor grounded in provided documents",
        },
        "classify_prompt": {
            "version": "1.0",
            "description": "Classifies questions into jd/resume/comparison/general",
        },
        "reformulate_prompt": {
            "version": "1.0",
            "description": "Rewrites queries for better retrieval on retry",
        },
        "agent_generate_prompt": {
            "version": "1.0",
            "description": "Generates answers with conversation history context",
        },
    }
