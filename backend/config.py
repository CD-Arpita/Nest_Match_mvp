"""
Central configuration.

Every other module reads settings from here rather than calling os.getenv()
directly, so there's exactly one place that knows about environment variables.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # no-op in production if there's no .env file; picks up local dev env

# --- AI provider: Groq (free, no card, open-source models) ------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-20b"

# --- Supabase -----------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# If Supabase credentials aren't set, the app falls back to a local JSON
# file store (data/local_store.json). This lets you run and demo the app
# immediately without provisioning a database first, then switch to
# Supabase for a real deployment just by setting two env vars.
USE_LOCAL_STORE = not (SUPABASE_URL and SUPABASE_KEY)

LOCAL_STORE_PATH = os.getenv(
    "LOCAL_STORE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "local_store.json"),
)


def require_groq_key() -> None:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file "
            "(local) or your deployment's secrets (Streamlit Cloud)."
        )
