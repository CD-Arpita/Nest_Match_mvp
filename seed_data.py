"""
Loads a handful of demo flatmate profiles so you can see ranked matches
immediately, without needing multiple real users. Safe to re-run --
profiles are upserted by id.

Usage:
    python seed_data.py
"""
from backend.db import save_profile
from backend.models import (
    Profile, SleepSchedule, CleanlinessLevel, GuestFrequency,
    FoodHabits, SmokingDrinking, WFHPattern,
)

DEMO_PROFILES = [
    Profile(
        name="Sakshi", age=24, city="Bengaluru",
        sleep_schedule=SleepSchedule.EARLY_BIRD,
        cleanliness_level=CleanlinessLevel.VERY_TIDY,
        guest_frequency=GuestFrequency.RARELY,
        food_habits=FoodHabits.VEGETARIAN,
        smoking_drinking=SmokingDrinking.NONE,
        wfh_pattern=WFHPattern.HYBRID,
        monthly_budget_inr=16000,
    ),
    Profile(
        name="Nayan", age=24, city="Pune",
        sleep_schedule=SleepSchedule.NIGHT_OWL,
        cleanliness_level=CleanlinessLevel.RELAXED,
        guest_frequency=GuestFrequency.FREQUENTLY,
        food_habits=FoodHabits.NON_VEGETARIAN,
        smoking_drinking=SmokingDrinking.SOCIAL_DRINKER,
        wfh_pattern=WFHPattern.FULL_OFFICE,
        monthly_budget_inr=14000,
    ),
    Profile(
        name="Gungun", age=25, city="Delhi",
        sleep_schedule=SleepSchedule.FLEXIBLE,
        cleanliness_level=CleanlinessLevel.VERY_TIDY,
        guest_frequency=GuestFrequency.OCCASIONALLY,
        food_habits=FoodHabits.EGGETARIAN,
        smoking_drinking=SmokingDrinking.NONE,
        wfh_pattern=WFHPattern.FULL_WFH,
        monthly_budget_inr=18000,
    ),
    Profile(
        name="Chunay", age=27, city="Mumbai",
        sleep_schedule=SleepSchedule.EARLY_BIRD,
        cleanliness_level=CleanlinessLevel.MODERATE,
        guest_frequency=GuestFrequency.RARELY,
        food_habits=FoodHabits.NON_VEGETARIAN,
        smoking_drinking=SmokingDrinking.NONE,
        wfh_pattern=WFHPattern.HYBRID,
        monthly_budget_inr=22000,
    ),
    Profile(
        name="Pranjali", age=25, city="Bengaluru",
        sleep_schedule=SleepSchedule.FLEXIBLE,
        cleanliness_level=CleanlinessLevel.MODERATE,
        guest_frequency=GuestFrequency.OCCASIONALLY,
        food_habits=FoodHabits.VEGETARIAN,
        smoking_drinking=SmokingDrinking.SOCIAL_DRINKER,
        wfh_pattern=WFHPattern.HYBRID,
        monthly_budget_inr=15000,
    ),
]

if __name__ == "__main__":
    for p in DEMO_PROFILES:
        save_profile(p)
        print(f"Seeded: {p.name} ({p.city})")
    print(f"\nDone \u2014 {len(DEMO_PROFILES)} demo profiles loaded.")
