"""
Orchestration layer.

This is the single seam between the Streamlit frontend and everything
else. app.py never imports ai_client or db directly -- it only calls
functions here. That keeps scoring logic in one auditable, testable
place, and means swapping the AI provider or the database later only
touches this file's callees, not the UI.
"""
from __future__ import annotations

from . import ai_client, db
from .models import Profile


def get_ranked_matches(me: Profile) -> list[dict]:
    """
    Compares `me` against every other stored profile and returns them
    ranked by compatibility score, highest first.

    Each result: {"profile": Profile, "score": int, "rationale": str}
    """
    candidates = [p for p in db.get_all_profiles() if p.id != me.id]

    results = []
    for candidate in candidates:
        cached = db.get_cached_score(me.id, candidate.id)
        if cached is not None:
            score, rationale = cached["score"], cached["rationale"]
        else:
            result = ai_client.score_pair(me, candidate)
            score, rationale = result["score"], result["rationale"]
            db.save_score(me.id, candidate.id, score, rationale)

        results.append({"profile": candidate, "score": score, "rationale": rationale})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def save_and_match(me: Profile) -> list[dict]:
    """Persists a (new or edited) profile, then returns its ranked matches."""
    db.save_profile(me)
    return get_ranked_matches(me)
