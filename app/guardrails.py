import re

# TODO: Add more LLM based rules to prevent prompt injection or forgetting the goal, Use agentic methods?

# Sensitive or confidential data to block
BLOCKED_KEYWORDS = [
    "salary", "payroll", "ssn", "social security", "password",
    "private key", "medical", "credit card", "classified", "top secret"
]

# Prevent general-purpose AI use unrelated to RAG domain
GENERAL_PURPOSE_PATTERNS = [
    r"\b(joke|story|weather|movie|recipe|translate|dream|poem|song|game)\b"
]

# Prevent prompt injection or forgetting the goal
INTENT_DRIFT_PATTERNS = [
    r"ignore (all|previous|earlier|these) instructions",
    r"forget (everything|your task|what i said)",
    r"let's talk about something else",
    r"you are now an assistant that",
    r"change your role",
    r"disregard your goal"
]

def is_query_allowed(query: str) -> bool:
    query_lower = query.lower()

    # Rule 1: Block sensitive terms
    if any(kw in query_lower for kw in BLOCKED_KEYWORDS):
        return False

    # Rule 2: Block general-purpose LLM drift
    for pattern in GENERAL_PURPOSE_PATTERNS + INTENT_DRIFT_PATTERNS:
        if re.search(pattern, query_lower):
            return False

    return True
