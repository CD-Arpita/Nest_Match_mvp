-- NestMatch MVP schema.
-- Run this in Supabase: Dashboard -> SQL Editor -> New query -> paste -> Run.
--
-- Deliberately minimal per the MVP's feasibility scoping: no auth tables,
-- no roles, no flat/listing tables. Just profiles and a score cache.

create table if not exists profiles (
    id uuid primary key,
    name text not null,
    age int not null,
    city text not null,
    sleep_schedule text not null,
    cleanliness_level text not null,
    guest_frequency text not null,
    food_habits text not null,
    smoking_drinking text not null,
    wfh_pattern text not null,
    monthly_budget_inr int not null,
    created_at timestamptz default now()
);

create table if not exists match_scores (
    pair_key text primary key,   -- two profile ids, sorted and joined with "|"
    score int not null check (score >= 0 and score <= 100),
    rationale text not null,
    created_at timestamptz default now()
);

-- MVP has no auth, so Row Level Security is left off for simplicity here.
-- Before any real (non-classroom) deployment, enable RLS and add policies
-- scoping reads/writes appropriately -- tracked in the roadmap as a V2 item.
