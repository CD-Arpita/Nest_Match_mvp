# NestMatch MVP

AI-powered flatmate-compatibility matching. Scoped exactly to the minimum
feature set from the Phase 2 deck:

1. Structured lifestyle profile creation (enum fields only)
2. Pairwise AI compatibility scoring (0–100)
3. Ranked candidate flatmate list
4. Plain-language match rationale display

**Not in this build (by design):** flat/property listings, owner
verification, in-app chat, payments, user authentication. See the
"Feasibility check" and "Roadmap" slides of the main deck for why.

**AI provider:** [Groq](https://groq.com) — genuinely free, no credit
card ever required, running the open-source Llama 3.3 model. Free tier
limits are generous enough for this MVP (30 requests/minute).

## Architecture

```
app.py (Streamlit UI)
   |
   v
backend/scoring.py      <- orchestration layer, the ONLY thing app.py calls
   |              |
   v              v
backend/ai_client.py   backend/db.py
   |                          |
   v                          v
 Groq API                Supabase (or local JSON fallback)
```

The frontend never calls the AI model or the database directly — every
match request goes through `scoring.py`. This is the same layered pattern
used in the earlier prototype, kept because it's what let a real bug
(enum serialization in the prompt builder) get caught and fixed in one
place without touching the UI, and it's also what made switching AI
providers (Claude → Groq) a one-file change instead of a rewrite.

## 1. Run it locally (fastest way to see it working)

You need Python 3.10+ and a free Groq API key.

```bash
cd nestmatch_mvp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# open .env and paste your GROQ_API_KEY
```

**Getting your free Groq key:**
1. Go to [console.groq.com](https://console.groq.com) and sign up (no
   credit card, ever).
2. Left sidebar → **API Keys** → **Create API Key**.
3. Copy the key (starts with `gsk_...`) and paste it into `.env` as
   `GROQ_API_KEY`.

Leave `SUPABASE_URL` and `SUPABASE_KEY` blank in `.env` for now — the app
will automatically run in **local demo mode**, storing profiles in
`data/local_store.json` instead of a real database. This is the fastest
way to confirm everything works before setting up Supabase.

```bash
python seed_data.py     # loads 5 demo flatmate profiles to match against
streamlit run app.py
```

Streamlit will open at `http://localhost:8501`. Fill in a profile and
click "Find my flatmate matches" — you should see a ranked list with
scores and rationales within a few seconds.

## 2. Set up Supabase (for a real deployment)

1. Go to [supabase.com](https://supabase.com) → New project (free tier is
   enough for this MVP).
2. Once it's provisioned: **SQL Editor** → New query → paste the contents
   of `supabase_schema.sql` → **Run**. This creates the `profiles` and
   `match_scores` tables.
3. **Project Settings → API** → copy the **Project URL** and the
   **anon public key**.
4. Put those into `.env` as `SUPABASE_URL` and `SUPABASE_KEY`.
5. Re-run `python seed_data.py` — it will now write to Supabase instead of
   the local file. Confirm the rows appear in **Table Editor → profiles**.

## 3. Deploy so the app runs online (Streamlit Community Cloud, free)

1. Push this folder to a **GitHub repository** (public or private).
   ```bash
   git init
   git add .
   git commit -m "NestMatch MVP"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
   `.env` is your local secrets file — **do not commit it**. Add a
   `.gitignore` with at least:
   ```
   .env
   venv/
   data/local_store.json
   __pycache__/
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with
   GitHub → **New app**.
3. Pick your repo, branch `main`, main file path `app.py` → **Deploy**.
4. Before (or right after) it builds, open **App → Settings → Secrets**
   and paste:
   ```toml
   GROQ_API_KEY = "gsk_..."
   GROQ_MODEL = "llama-3.3-70b-versatile"
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "eyJ..."
   ```
   Streamlit Cloud injects Secrets as environment variables automatically
   — `backend/config.py` picks them up the same way it reads your local
   `.env`, no code changes needed.
5. Once it redeploys, run `seed_data.py` once against the **same**
   Supabase project (from your machine, with `.env` pointing at it) so the
   live app has demo profiles to match against.
6. Your app is now live at `https://<your-app-name>.streamlit.app`.

### Alternative: any Docker-friendly host (Render, Railway, Fly.io, etc.)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Save that as `Dockerfile` in this folder, then follow your host's normal
"deploy from GitHub / Dockerfile" flow, setting the same four environment
variables as Secrets there.

## Project structure

```
nestmatch_mvp/
├── app.py                   # Streamlit UI (only calls backend.scoring)
├── seed_data.py              # loads demo profiles for the ranked list
├── supabase_schema.sql       # run once in Supabase SQL Editor
├── requirements.txt
├── .env.example
├── data/
│   └── local_store.json      # auto-created in local demo mode
└── backend/
    ├── config.py              # env vars, local-vs-Supabase switch
    ├── models.py               # Profile dataclass + enums
    ├── prompts.py               # system prompt + forced-tool schema
    ├── ai_client.py              # the only module that calls Groq
    ├── db.py                      # the only module that touches storage
    └── scoring.py                  # orchestration seam used by app.py
```

## Extending it (see the roadmap slide for the full plan)

- **V2**: verified profiles / safety layer, in-app chat, real user auth,
  freemium pricing test.
- **V3**: owner-facing flat-listing module (separate product line —
  requires owner consent flows, kept deliberately out of this codebase).
- **Switching AI providers again**: everything the AI does lives in
  `backend/ai_client.py` and `backend/prompts.py`. Want to move to Claude,
  Gemini, or something self-hosted later? Only those two files change.

Adding features should mean adding new backend modules, not routing new
logic through `app.py` — keep the frontend/orchestration boundary intact.
