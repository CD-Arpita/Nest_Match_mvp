"""
Prompt construction for the compatibility-scoring capability.

The weighting guidance below encodes the pain axes named repeatedly across
the 5 user interviews behind this product (sleep, cleanliness, guests,
food, financial reliability) rather than treating every field as equally
important by default.
"""
from .models import Profile

SYSTEM_PROMPT = """You are NestMatch's flatmate-compatibility engine.

You will be given two structured lifestyle profiles for people who may
share a flat. Score how compatible they are as flatmates and explain why,
using ONLY the structured fields provided \u2014 never invent details that
aren't in the profiles.

Weighting guidance, grounded in user research on the biggest sources of
flatmate conflict:
- Sleep schedule and cleanliness level are the most common source of daily
  friction \u2014 weight mismatches here heavily.
- Guest frequency mismatches (one person hosting often, the other wanting
  quiet) are a close second.
- Food habits matter most when they're strongly opposed (e.g. one profile
  is vegetarian and the other frequently cooks meat in a shared kitchen);
  otherwise weight lightly.
- Smoking/drinking mismatches matter if one person is fully non-smoking/
  non-drinking and the other is a smoker \u2014 otherwise weight lightly.
- WFH pattern affects how much shared daytime space is used \u2014 weight
  moderately.
- Budget: treat two monthly figures within ~20% of each other as
  compatible; a larger gap suggests a real affordability mismatch worth
  flagging in the rationale.

Always call the score_compatibility tool with your result. Do not respond
in plain text.

The rationale must be 2\u20133 plain-language sentences a non-technical person
would understand, written for the two people being matched \u2014 not a list
of field-by-field comparisons. Name the one or two factors that mattered
most to your score."""


def format_profile(label: str, p: Profile) -> str:
    return (
        f"{label}: {p.name}, {p.age}, based in {p.city}\n"
        f"  Sleep schedule: {p.sleep_schedule.value}\n"
        f"  Cleanliness: {p.cleanliness_level.value}\n"
        f"  Guests: {p.guest_frequency.value}\n"
        f"  Food habits: {p.food_habits.value}\n"
        f"  Smoking/drinking: {p.smoking_drinking.value}\n"
        f"  Work pattern: {p.wfh_pattern.value}\n"
        f"  Monthly budget: \u20b9{p.monthly_budget_inr:,}"
    )


def build_user_message(profile_a: Profile, profile_b: Profile) -> str:
    return (
        "Score the compatibility of these two flatmate candidates.\n\n"
        f"{format_profile('Profile A', profile_a)}\n\n"
        f"{format_profile('Profile B', profile_b)}"
    )


# The tool schema that forces structured output. tool_choice locks the model
# into calling exactly this tool, so the response is always a parseable
# {score, rationale} object -- never free text to regex out. Groq's API is
# OpenAI-compatible, so tools are declared in the {"type": "function", ...}
# shape rather than Anthropic's flatter {"name": ..., "input_schema": ...}.
SCORE_TOOL = {
    "type": "function",
    "function": {
        "name": "score_compatibility",
        "description": "Report the flatmate compatibility score and rationale for the two profiles.",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Compatibility score from 0 (very poor fit) to 100 (excellent fit).",
                },
                "rationale": {
                    "type": "string",
                    "description": "2-3 plain-language sentences explaining the score to both users.",
                },
            },
            "required": ["score", "rationale"],
        },
    },
}
