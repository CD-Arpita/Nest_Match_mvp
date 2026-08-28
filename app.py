"""
NestMatch MVP -- Streamlit frontend.

Feature set (matches the minimum feature set in the Phase 2 deck):
  1. Structured lifestyle profile creation (enum fields only)
  2. Pairwise AI compatibility scoring (0-100)
  3. Ranked candidate flatmate list
  4. Plain-language match rationale display

Scope boundary: this app matches PEOPLE, not flats. There is no listing,
no owner role, no verification -- see the "Scoping" slide of the main
deck for why that's a deliberate decision, not an oversight.

This file only ever imports from `backend.scoring` -- never
`backend.ai_client` or `backend.db` directly. That boundary is the
architecture, not a style preference.
"""
import streamlit as st

from backend import config
from backend.models import (
    Profile, SleepSchedule, CleanlinessLevel, GuestFrequency,
    FoodHabits, SmokingDrinking, WFHPattern,
)
from backend.scoring import save_and_match

st.set_page_config(page_title="NestMatch", page_icon="\U0001F3E1", layout="centered")

st.title("\U0001F3E1 NestMatch")
st.caption("Find a flatmate who actually fits \u2014 scored and explained by AI, not just listed.")

if config.USE_LOCAL_STORE:
    st.info(
        "Running in **local demo mode** (no Supabase configured) \u2014 profiles are "
        "saved to a local file, not a real database. Set `SUPABASE_URL` and "
        "`SUPABASE_KEY` to switch to Supabase. See README.md.",
        icon="\u2139\ufe0f",
    )

st.divider()
st.subheader("Your lifestyle profile")
st.caption("Structured fields only \u2014 no free text, no photos. This keeps every profile equally comparable and avoids self-presentation bias.")

with st.form("profile_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="e.g. Aditi")
        age = st.number_input("Age", min_value=18, max_value=65, value=24)
        city = st.text_input("City you're moving to / living in", placeholder="e.g. Bengaluru")
        monthly_budget_inr = st.number_input(
            "Your monthly rent budget (\u20b9)", min_value=2000, max_value=100000, value=15000, step=1000
        )
    with col2:
        sleep_schedule = st.selectbox("Sleep schedule", [e.value for e in SleepSchedule])
        cleanliness_level = st.selectbox("Cleanliness", [e.value for e in CleanlinessLevel])
        guest_frequency = st.selectbox("Guests", [e.value for e in GuestFrequency])
        food_habits = st.selectbox("Food habits", [e.value for e in FoodHabits])
        smoking_drinking = st.selectbox("Smoking / drinking", [e.value for e in SmokingDrinking])
        wfh_pattern = st.selectbox("Work pattern", [e.value for e in WFHPattern])

    submitted = st.form_submit_button("Find my flatmate matches", use_container_width=True, type="primary")

if submitted:
    if not name or not city:
        st.error("Please fill in your name and city.")
        st.stop()

    me = Profile(
        name=name,
        age=int(age),
        city=city,
        sleep_schedule=SleepSchedule(sleep_schedule),
        cleanliness_level=CleanlinessLevel(cleanliness_level),
        guest_frequency=GuestFrequency(guest_frequency),
        food_habits=FoodHabits(food_habits),
        smoking_drinking=SmokingDrinking(smoking_drinking),
        wfh_pattern=WFHPattern(wfh_pattern),
        monthly_budget_inr=int(monthly_budget_inr),
    )

    with st.spinner("Scoring compatibility against candidate flatmates\u2026"):
        try:
            matches = save_and_match(me)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()

    st.divider()
    if not matches:
        st.warning(
            "No other profiles to match against yet. Run `python seed_data.py` "
            "to load demo candidates, then try again."
        )
    else:
        st.subheader(f"Ranked matches for {me.name}")
        for m in matches:
            p, score, rationale = m["profile"], m["score"], m["rationale"]
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{p.name}**, {p.age} \u00b7 {p.city}")
                    st.caption(
                        f"{p.sleep_schedule.value} \u00b7 {p.cleanliness_level.value} \u00b7 "
                        f"Budget \u20b9{p.monthly_budget_inr:,}"
                    )
                with c2:
                    st.metric("Compatibility", f"{score}/100")
                st.write(rationale)

st.divider()
st.caption(
    "NestMatch MVP \u00b7 flatmate-compatibility matching only \u2014 no flat listings, "
    "no owner verification (see the roadmap for why)."
)
