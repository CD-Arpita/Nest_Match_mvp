"""
Thin wrapper around the Groq SDK.

This is the ONLY module that talks to the AI provider.
Nothing else in the app should import groq directly.
"""

from dotenv import load_dotenv

load_dotenv()

import json

from groq import Groq

from . import config
from .models import Profile
from .prompts import SYSTEM_PROMPT, SCORE_TOOL, build_user_message


_client = None


def _get_client() -> Groq:
    """Create and return the Groq client."""
    global _client

    if _client is None:
        config.require_groq_key()
        _client = Groq(api_key=config.GROQ_API_KEY)

    return _client


def score_pair(profile_a: Profile, profile_b: Profile) -> dict:
    """
    Score compatibility between two flatmate profiles.

    Returns:
        {
            "score": int,
            "rationale": str
        }
    """

    client = _get_client()

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_user_message(
                    profile_a,
                    profile_b,
                ),
            },
        ],

        tools=[SCORE_TOOL],

        # Let the model decide to use the tool.
        # The prompt/tool definition will guide it.
        tool_choice="auto",

        max_completion_tokens=1000,

        temperature=0.2,
    )

    message = response.choices[0].message

    tool_calls = message.tool_calls or []

    # Find the score_compatibility call
    for call in tool_calls:

        if call.function.name == "score_compatibility":

            try:
                result = json.loads(call.function.arguments)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    "Groq returned invalid JSON arguments: "
                    + str(call.function.arguments)
                ) from e

            try:
                score = int(result["score"])
            except (KeyError, TypeError, ValueError) as e:
                raise RuntimeError(
                    f"Groq returned an invalid score: {result}"
                ) from e

            # Defensive clamp
            score = max(0, min(100, score))

            rationale = str(
                result.get("rationale", "")
            ).strip()

            if not rationale:
                rationale = (
                    "Compatibility score generated from the two profiles."
                )

            return {
                "score": score,
                "rationale": rationale,
            }

    # If the model did not call the tool, fail clearly.
    raise RuntimeError(
        "Groq did not return the expected "
        "score_compatibility tool call.\n\n"
        f"Model response: {message}"
    )
