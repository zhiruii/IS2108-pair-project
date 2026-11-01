import numpy as np
import pandas as pd

from accounts.models import LEVEL_CHOICES, QUALIFICATION_CHOICES
from listings.models import Listing
from .pipeline import is_weekend, time_band

# Every pricing assumption lives here, so the whole thing can be shown in the report.
# Reference tutor (all multipliers = 1.0): DEGREE, 0 years, in person,
# weekday afternoon, languages/humanities subject. Figures are SGD per hour.
# Anchored to published Singapore agency guides (Tutopiya, TutorCity, MindFlex);
# the weekend/evening and experience figures are assumptions, not published.
RATE_RULES = {
    "base_by_level": {
        "P1": 38, "P2": 38, "P3": 40, "P4": 42, "P5": 44, "P6": 50,
        "S1": 46, "S2": 46, "S3": 52, "S4": 56, "S5": 56,
        "JC1": 70, "JC2": 78,
    },
    "qualification": {
        "STUDENT": 0.72, "DIPLOMA": 0.85, "DEGREE": 1.00,
        "POSTGRAD": 1.12, "NIE": 1.30, "OTHER": 0.85,
    },
    # +1.5% a year for years 1-5, +1% a year for years 6-10, nothing after 10
    "experience": {"early_rate": 0.015, "later_rate": 0.010},
    "subject": {
        "ENGLISH": 1.00, "CHINESE": 1.00, "MALAY": 1.00, "TAMIL": 1.00,
        "GEOGRAPHY": 1.00, "HISTORY": 1.00, "LITERATURE": 1.00,
        "MATH": 1.08, "SCIENCE": 1.08, "BIOLOGY": 1.08, "ECONOMICS": 1.08,
        "E_MATH": 1.15, "A_MATH": 1.15, "PHYSICS": 1.15, "CHEMISTRY": 1.15,
        "H2_MATH": 1.20,
    },
    "mode": {"IN_PERSON": 1.00, "HYBRID": 0.95, "ONLINE": 0.90},
    "weekend": 1.06,
    "time_band": {"MORNING": 0.98, "AFTERNOON": 1.00, "EVENING": 1.04},
    "noise_sigma": 0.10,   # about +/-10% random variation between tutors
    "round_to": 5,         # tutors quote round numbers
    "floor": 15,
    "ceiling": 200,
}

# Which subjects are realistic at which level. All 16 subjects and all 13 levels appear.
_PRIMARY = ["ENGLISH", "CHINESE", "MALAY", "TAMIL", "MATH", "SCIENCE"]
_LOWER_SEC = _PRIMARY + ["GEOGRAPHY", "HISTORY", "LITERATURE"]
_UPPER_SEC = ["ENGLISH", "CHINESE", "MALAY", "TAMIL", "E_MATH", "A_MATH", "SCIENCE",
              "PHYSICS", "CHEMISTRY", "BIOLOGY", "GEOGRAPHY", "HISTORY", "LITERATURE"]
_JC = ["ENGLISH", "CHINESE", "H2_MATH", "PHYSICS", "CHEMISTRY", "BIOLOGY",
       "ECONOMICS", "GEOGRAPHY", "HISTORY", "LITERATURE"]

SUBJECTS_BY_LEVEL = {
    **{lvl: _PRIMARY for lvl in ("P1", "P2", "P3", "P4", "P5", "P6")},
    **{lvl: _LOWER_SEC for lvl in ("S1", "S2")},
    **{lvl: _UPPER_SEC for lvl in ("S3", "S4", "S5")},
    **{lvl: _JC for lvl in ("JC1", "JC2")},
}

# Who the simulated tutors are (not pricing rules, so kept apart from RATE_RULES).
QUALIFICATION_MIX = {  # share of tutors
    "STUDENT": 0.30, "DIPLOMA": 0.08, "DEGREE": 0.30,
    "POSTGRAD": 0.08, "NIE": 0.16, "OTHER": 0.08,
}
YEARS_BY_QUALIFICATION = {  # (min, max) years of experience, so a student can't have 20 years
    "STUDENT": (0, 3), "DIPLOMA": (0, 8), "DEGREE": (0, 12),
    "POSTGRAD": (0, 15), "NIE": (3, 25), "OTHER": (0, 10),
}
MODE_MIX = {"IN_PERSON": 0.5, "ONLINE": 0.3, "HYBRID": 0.2}


def check_rules_cover_app():
    # fail loudly if the app gains a category the rules don't know about
    app_levels = {code for code, _ in LEVEL_CHOICES}
    app_subjects = {code for code, _ in Listing.SUBJECT_CHOICES}
    app_modes = {code for code, _ in Listing.MODE_CHOICES}
    app_quals = {code for code, _ in QUALIFICATION_CHOICES}
    problems = []
    if app_levels != set(RATE_RULES["base_by_level"]):
        problems.append("levels")
    if app_subjects != set(RATE_RULES["subject"]):
        problems.append("subjects")
    if app_modes != set(RATE_RULES["mode"]):
        problems.append("modes")
    if app_quals != set(RATE_RULES["qualification"]):
        problems.append("qualifications")
    if problems:
        raise ValueError("RATE_RULES is out of step with the app: " + ", ".join(problems))


def experience_multiplier(years):
    early = min(years, 5) * RATE_RULES["experience"]["early_rate"]
    later = max(min(years, 10) - 5, 0) * RATE_RULES["experience"]["later_rate"]
    return 1 + early + later


def expected_rate(level, subject, mode, qualification, years_experience, weekday, start_hour):
    # the noise-free price: just the multipliers applied one after another
    rules = RATE_RULES
    rate = rules["base_by_level"][level]
    rate *= rules["qualification"][qualification]
    rate *= experience_multiplier(years_experience)
    rate *= rules["subject"][subject]
    rate *= rules["mode"][mode]
    if is_weekend(weekday):
        rate *= rules["weekend"]
    rate *= rules["time_band"][time_band(start_hour)]
    return rate


def generate_dataset(n=5000, seed=42):
    check_rules_cover_app()
    rng = np.random.default_rng(seed)   # fixed seed -> same data every run

    levels = [code for code, _ in LEVEL_CHOICES]
    quals = list(QUALIFICATION_MIX)
    qual_p = list(QUALIFICATION_MIX.values())
    modes = list(MODE_MIX)
    mode_p = list(MODE_MIX.values())

    rows = []
    for _ in range(n):
        level = str(rng.choice(levels))
        subject = str(rng.choice(SUBJECTS_BY_LEVEL[level]))
        qualification = str(rng.choice(quals, p=qual_p))
        low, high = YEARS_BY_QUALIFICATION[qualification]
        years = int(rng.integers(low, high + 1))
        mode = str(rng.choice(modes, p=mode_p))
        weekday = int(rng.integers(0, 7))
        # school hours rule out weekday mornings; weekends can start earlier
        start_hour = int(rng.integers(9, 19)) if is_weekend(weekday) else int(rng.integers(14, 21))

        rate = expected_rate(level, subject, mode, qualification, years, weekday, start_hour)
        rate *= rng.lognormal(0, RATE_RULES["noise_sigma"])   # random +/- variation
        step = RATE_RULES["round_to"]
        rate = round(rate / step) * step
        rate = min(max(rate, RATE_RULES["floor"]), RATE_RULES["ceiling"])

        rows.append({
            "level": level,
            "subject": subject,
            "mode": mode,
            "qualification": qualification,
            "years_experience": years,
            "weekday": weekday,
            "start_hour": start_hour,
            "rate_per_hour": rate,
        })

    return pd.DataFrame(rows)
