"""
Structured lifestyle profile model.

Deliberately enum/typed-integer only, no free text and no photos. This is a
product decision (see the "compatibility score basis" slide of the main
deck): free-text bios and photos are prone to self-presentation bias and
image filtering, which the AI can't correct for. Fixed enums keep the
signal comparable across users and keep the AI's job well-defined: compare
structured attributes, don't interpret prose.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class SleepSchedule(str, Enum):
    EARLY_BIRD = "Early bird (asleep before 11pm, up before 7am)"
    FLEXIBLE = "Flexible / no fixed schedule"
    NIGHT_OWL = "Night owl (up past 1am regularly)"


class CleanlinessLevel(str, Enum):
    VERY_TIDY = "Very tidy \u2014 clean daily, everything has a place"
    MODERATE = "Moderate \u2014 clean common areas weekly"
    RELAXED = "Relaxed \u2014 clean when it visibly needs it"


class GuestFrequency(str, Enum):
    RARELY = "Rarely have guests over"
    OCCASIONALLY = "Occasional guests (few times a month)"
    FREQUENTLY = "Frequent guests / regularly host"


class FoodHabits(str, Enum):
    VEGETARIAN = "Vegetarian"
    EGGETARIAN = "Eggetarian"
    NON_VEGETARIAN = "Non-vegetarian"
    VEGAN = "Vegan"


class SmokingDrinking(str, Enum):
    NONE = "Non-smoker, non-drinker"
    SOCIAL_DRINKER = "Social drinker, non-smoker"
    SMOKER = "Smoker"
    BOTH = "Smoker and drinker"


class WFHPattern(str, Enum):
    FULL_WFH = "Fully work-from-home"
    HYBRID = "Hybrid (some days from home)"
    FULL_OFFICE = "Fully in-office"


# Budget is a typed integer (monthly share, INR) rather than an enum bucket,
# since it's a genuinely continuous value and the AI can reason about
# closeness directly instead of coarse bucket-matching.

@dataclass
class Profile:
    name: str
    age: int
    city: str
    sleep_schedule: SleepSchedule
    cleanliness_level: CleanlinessLevel
    guest_frequency: GuestFrequency
    food_habits: FoodHabits
    smoking_drinking: SmokingDrinking
    wfh_pattern: WFHPattern
    monthly_budget_inr: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        d = asdict(self)
        # Enums serialize to their .value automatically via asdict() only if
        # they're plain values already; store the .value explicitly to avoid
        # the enum-object-vs-string bug class this app is designed to avoid.
        for enum_field in (
            "sleep_schedule", "cleanliness_level", "guest_frequency",
            "food_habits", "smoking_drinking", "wfh_pattern",
        ):
            val = d[enum_field]
            d[enum_field] = val.value if isinstance(val, Enum) else val
        return d

    @staticmethod
    def from_dict(d: dict) -> "Profile":
        return Profile(
            id=d.get("id", str(uuid.uuid4())),
            name=d["name"],
            age=int(d["age"]),
            city=d["city"],
            sleep_schedule=SleepSchedule(d["sleep_schedule"]),
            cleanliness_level=CleanlinessLevel(d["cleanliness_level"]),
            guest_frequency=GuestFrequency(d["guest_frequency"]),
            food_habits=FoodHabits(d["food_habits"]),
            smoking_drinking=SmokingDrinking(d["smoking_drinking"]),
            wfh_pattern=WFHPattern(d["wfh_pattern"]),
            monthly_budget_inr=int(d["monthly_budget_inr"]),
        )
