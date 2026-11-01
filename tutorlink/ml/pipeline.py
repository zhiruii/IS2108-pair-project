from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

# where the trained model is saved; the train command writes it, predict.py reads it
MODEL_PATH = Path(__file__).resolve().parent / "price_model.joblib"

# Shared feature rules. The data generator and the model pipeline both use these, so the weekend flag and time band can never disagree between training and prediction.

def is_weekend(weekday):
    # Listing.weekday: 0 = Monday ... 5 = Saturday, 6 = Sunday
    return weekday >= 5


def time_band(hour):
    # a band is easier for the model to learn than 24 separate hours
    if hour < 12:
        return "MORNING"
    if hour < 17:
        return "AFTERNOON"
    return "EVENING"


# The raw fields the app passes in, as columns of a one-row table.
RAW_COLUMNS = ["level", "subject", "mode", "qualification",
               "years_experience", "weekday", "start_hour"]

CATEGORICAL = ["level", "subject", "mode", "qualification", "time_band"]
NUMERIC = ["years_capped", "is_weekend"]


def add_features(df):
    # derive the model's features from the raw fields
    df = df.copy()
    df["is_weekend"] = df["weekday"].map(is_weekend).astype(int)
    df["time_band"] = df["start_hour"].map(time_band)
    # pay stops rising after about 10 years, so a straight line through 25 years would mislead
    df["years_capped"] = df["years_experience"].clip(upper=10)
    return df


def build_pipeline(model):
    # one object: raw table in -> prediction out
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("num", "passthrough", NUMERIC),
    ])
    return Pipeline([
        ("features", FunctionTransformer(add_features)),
        ("prep", prep),
        ("model", model),
    ])
