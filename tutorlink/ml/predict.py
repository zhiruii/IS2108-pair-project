import joblib
import numpy as np
import pandas as pd

from .pipeline import MODEL_PATH, RAW_COLUMNS

VERDICT_LABELS = {
    "BELOW": "Below estimate",
    "FAIR": "Fair",
    "ABOVE": "Above estimate",
}

_artifact = None


def load_model():
    # load the joblib once per process; None if it hasn't been trained yet
    global _artifact
    if _artifact is None and MODEL_PATH.exists():
        _artifact = joblib.load(MODEL_PATH)
    return _artifact


def predict_ranges(rows):
    # rows: list of dicts with level, subject, mode, qualification, years_experience,
    # weekday and start_time (a time object) -> list of (low, high) whole dollars
    artifact = load_model()
    if artifact is None or not rows:
        return [None] * len(rows)
    table = pd.DataFrame(rows)
    table["start_hour"] = [t.hour for t in table["start_time"]]
    table = table[RAW_COLUMNS]
    mid = np.exp(artifact["pipeline"].predict(table))
    low = np.maximum(mid * np.exp(-artifact["band"]), artifact["floor"])
    high = np.minimum(mid * np.exp(artifact["band"]), artifact["ceiling"])
    # round outwards
    return [(int(np.floor(lo)), int(np.ceil(hi))) for lo, hi in zip(low, high)]


def listing_fields(listing):
    # a Listing (with its TutorProfile) as the row the model expects
    return {
        "level": listing.level, "subject": listing.subject, "mode": listing.mode,
        "qualification": listing.tutor.qualification,
        "years_experience": listing.tutor.years_experience,
        "weekday": listing.weekday, "start_time": listing.start_time,
    }


def ranges_for_listings(listings):
    # one model call for many listings (the parent page and the staff page need this)
    return predict_ranges([listing_fields(listing) for listing in listings])


def verdict(rate, price_range):
    # BELOW / FAIR / ABOVE for a rate against (low, high); None if there is no range
    if price_range is None:
        return None
    low, high = price_range
    rate = float(rate)
    if rate < low:
        return "BELOW"
    if rate > high:
        return "ABOVE"
    return "FAIR"
