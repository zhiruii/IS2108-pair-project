import joblib
import numpy as np
import sklearn
from django.core.management.base import BaseCommand
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from ml.generator import RATE_RULES, generate_dataset
from ml.pipeline import MODEL_PATH, RAW_COLUMNS, build_pipeline

TEST_SIZE = 0.2          # share of rows held back to judge the model fairly
BAND_QUANTILE = 0.80     # the range should contain about 80% of unseen prices


class Command(BaseCommand):
    help = "Generate simulated listings, train the Ridge price model and save it to ml/price_model.joblib"

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, default=5000)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        seed = options["seed"]
        df = generate_dataset(options["rows"], seed)
        X = df[RAW_COLUMNS]
        y = np.log(df["rate_per_hour"])   # predict log price, so effects are multiplicative

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=seed
        )

        pipe = build_pipeline(Ridge(alpha=1.0))
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)

        mae = float(mean_absolute_error(np.exp(y_test), np.exp(pred)))   # dollars
        r2 = float(r2_score(y_test, pred))                               # on log price
        self.stdout.write(f"Ridge   MAE ${mae:.2f}   R2 {r2:.3f}")

        # range band: the 80th percentile of the size of the error on unseen rows
        residuals = y_test.to_numpy() - pred
        band = float(np.quantile(np.abs(residuals), BAND_QUANTILE))
        covered = float(np.mean(np.abs(residuals) <= band))
        self.stdout.write(f"Band: x/ {np.exp(band):.3f} (about +/-{(np.exp(band) - 1) * 100:.0f}%), "
                          f"covers {covered * 100:.0f}% of test rows")

        self.show_learned_effects(pipe)

        artifact = {
            "pipeline": pipe,
            "model_name": "ridge",
            "band": band,
            "floor": RATE_RULES["floor"],
            "ceiling": RATE_RULES["ceiling"],
            "metrics": {"mae": mae, "r2": r2},
            "n_rows": len(df),
            "seed": seed,
            "sklearn_version": sklearn.__version__,
        }
        joblib.dump(artifact, MODEL_PATH)
        self.stdout.write(f"Saved {MODEL_PATH}")

    def show_learned_effects(self, pipe):
        # compare what Ridge learned with the multipliers we put into the data
        names = pipe.named_steps["prep"].get_feature_names_out()
        coef = dict(zip(names, pipe.named_steps["model"].coef_))
        self.stdout.write("\nRule vs learned multiplier (Ridge):")

        def row(label, rule, learned):
            self.stdout.write(f"  {label:22} rule {rule:.2f}   learned {learned:.2f}")

        references = {"qualification": "DEGREE", "mode": "IN_PERSON", "subject": "ENGLISH"}
        for group, ref in references.items():
            for category, rule in RATE_RULES[group].items():
                if category == ref:
                    continue
                learned = np.exp(coef[f"cat__{group}_{category}"] - coef[f"cat__{group}_{ref}"])
                row(f"{group} {category}", rule / RATE_RULES[group][ref], learned)

        row("weekend", RATE_RULES["weekend"], np.exp(coef["num__is_weekend"]))
        row("evening vs afternoon", RATE_RULES["time_band"]["EVENING"],
            np.exp(coef["cat__time_band_EVENING"] - coef["cat__time_band_AFTERNOON"]))
        self.stdout.write(f"  experience: +{(np.exp(coef['num__years_capped']) - 1) * 100:.2f}% per year up to 10 "
                          f"(rule averages about 1.25%)")

