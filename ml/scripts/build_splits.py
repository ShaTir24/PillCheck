"""Stratified train/val/test split registry, BY PILL TYPE not by image —
PRD §11.3: "no appearance-class leakage across splits."

Note: this is for OUR OWN future training splits (Phase 1 encoder training
needs a train/val cut). It does NOT re-split ePillID's benchmark images —
eval/harness.py uses ePillID's own official fold CSVs as-is, since that's
the fixed protocol being reproduced for baseline comparison (see
data/manifests/epillid.json).
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def build_splits(
    pilltype_ids: np.ndarray, seed: int, ratios: tuple[float, float, float] = (0.8, 0.1, 0.1)
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    unique_types = np.array(sorted(set(pilltype_ids)))
    rng.shuffle(unique_types)

    n = len(unique_types)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])

    split_of = {}
    split_of.update({t: "train" for t in unique_types[:n_train]})
    split_of.update({t: "val" for t in unique_types[n_train : n_train + n_val]})
    split_of.update({t: "test" for t in unique_types[n_train + n_val :]})

    return pd.DataFrame({"pilltype_id": unique_types, "split": [split_of[t] for t in unique_types]})


def assert_no_leakage(splits_df: pd.DataFrame) -> None:
    counts = splits_df.groupby("pilltype_id")["split"].nunique()
    leaked = counts[counts > 1]
    if len(leaked) > 0:
        raise AssertionError(f"{len(leaked)} pill types appear in more than one split")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROCESSED_DIR / "epillid_ndc_joined.csv"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"{input_path} missing — run scripts/join_metadata.py first")

    df = pd.read_csv(input_path)
    splits_df = build_splits(df.pilltype_id.to_numpy(), seed=args.seed)
    assert_no_leakage(splits_df)

    counts = splits_df["split"].value_counts()
    print(f"pill types: {len(splits_df)} total -> {counts.to_dict()}")

    out_path = PROCESSED_DIR / "split_registry.csv"
    splits_df.to_csv(out_path, index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
