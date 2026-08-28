"""
Persistence layer.

Nothing outside this module talks to Supabase (or the local JSON
fallback) directly -- same seam principle as ai_client.py. Two
responsibilities: profiles (structured lifestyle data) and a score cache
(so re-viewing the same match list doesn't re-call the AI model and re-spend
tokens on a pair we've already scored).

MVP scope: no auth, no multi-user roles, no row-level security. Every
profile is visible to every session -- fine for a seeded demo, NOT what
you'd ship broadly (see the roadmap in the main deck for V2 auth/roles).
"""
from __future__ import annotations

import json
import os
import threading
from typing import Optional

from . import config
from .models import Profile

_lock = threading.Lock()


# ---------------------------------------------------------------- local mode
def _read_local_store() -> dict:
    if not os.path.exists(config.LOCAL_STORE_PATH):
        return {"profiles": [], "scores": {}}
    with open(config.LOCAL_STORE_PATH, "r") as f:
        return json.load(f)


def _write_local_store(data: dict) -> None:
    os.makedirs(os.path.dirname(config.LOCAL_STORE_PATH), exist_ok=True)
    with open(config.LOCAL_STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _score_key(id_a: str, id_b: str) -> str:
    # Canonicalize so (A, B) and (B, A) hit the same cache entry.
    return "|".join(sorted([id_a, id_b]))


# ---------------------------------------------------------------- supabase mode
def _get_supabase_client():
    from supabase import create_client
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


# ---------------------------------------------------------------- public API
def get_all_profiles() -> list[Profile]:
    if config.USE_LOCAL_STORE:
        data = _read_local_store()
        return [Profile.from_dict(p) for p in data["profiles"]]
    client = _get_supabase_client()
    res = client.table("profiles").select("*").execute()
    return [Profile.from_dict(p) for p in res.data]


def save_profile(profile: Profile) -> None:
    if config.USE_LOCAL_STORE:
        with _lock:
            data = _read_local_store()
            data["profiles"] = [
                p for p in data["profiles"] if p["id"] != profile.id
            ]
            data["profiles"].append(profile.to_dict())
            _write_local_store(data)
        return
    client = _get_supabase_client()
    client.table("profiles").upsert(profile.to_dict()).execute()


def get_cached_score(id_a: str, id_b: str) -> Optional[dict]:
    if config.USE_LOCAL_STORE:
        data = _read_local_store()
        return data["scores"].get(_score_key(id_a, id_b))
    client = _get_supabase_client()
    key = _score_key(id_a, id_b)
    res = (
        client.table("match_scores")
        .select("*")
        .eq("pair_key", key)
        .execute()
    )
    if res.data:
        row = res.data[0]
        return {"score": row["score"], "rationale": row["rationale"]}
    return None


def save_score(id_a: str, id_b: str, score: int, rationale: str) -> None:
    key = _score_key(id_a, id_b)
    if config.USE_LOCAL_STORE:
        with _lock:
            data = _read_local_store()
            data["scores"][key] = {"score": score, "rationale": rationale}
            _write_local_store(data)
        return
    client = _get_supabase_client()
    client.table("match_scores").upsert(
        {"pair_key": key, "score": score, "rationale": rationale}
    ).execute()
