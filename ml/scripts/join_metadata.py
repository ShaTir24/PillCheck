"""Join NDC product identity onto ePillID images by package NDC (PRD §11.2
ReferenceAppearance mapping: drug_name/strength/form <-> NDC directory fields).

ePillID's `pilltype_id` embeds a package NDC as its prefix (e.g.
"51285-0092-87_BE305F72" -> package_ndc "51285-0092-87", confirmed by
inspecting real downloaded rows) — that's the join key into the NDC
directory's `packaging[].package_ndc`.

Known gaps, both confirmed empirically (not assumed):
1. SPLIMPRINT/SPLSHAPE/SPLCOLOR/SPLSIZE/SPLSCORE (Pillbox fields) are NOT in
   the openFDA NDC directory — confirmed by inspecting a live record, those
   fields simply aren't present there. Pillbox's own bulk metadata download
   isn't resolved yet (see data/manifests/pillbox.json). This script leaves
   those columns null; it does not fabricate values.
2. The live openFDA NDC directory only lists currently-marketed products, and
   ePillID's images are ~2016-2018 vintage (sourced from the now-discontinued
   Pillbox pilot) — most of those exact package NDCs have since been
   delisted. Measured: ~0.5% of ePillID's package NDCs are still live in the
   2026 NDC export (checked at both package_ndc and product_ndc granularity).
   This join is still correct and useful for FR-5 (a user adding a CURRENT
   prescription's NDC) — it just can't backfill historical ePillID images.
   Real appearance metadata for those specific images has to come from
   Pillbox's own (archived) per-pill records, not the live NDC directory.
"""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EPILLID_FOLDS_DIR = (
    RAW_DIR / "epillid/ePillID_data/folds/pilltypeid_nih_sidelbls0.01_metric_5folds/base"
)
FOLD_PREFIX = "pilltypeid_nih_sidelbls0.01_metric_5folds"


def build_ndc_lookup() -> dict[str, dict]:
    ndc_files = list((RAW_DIR / "ndc").glob("*.json"))
    if not ndc_files:
        raise FileNotFoundError("no NDC json found — run scripts/download_ndc.py first")

    with open(ndc_files[0]) as f:
        records = json.load(f)["results"]

    lookup: dict[str, dict] = {}
    for r in records:
        fields = {
            "generic_name": r.get("generic_name"),
            "brand_name": r.get("brand_name"),
            "dosage_form": r.get("dosage_form"),
            "product_ndc": r.get("product_ndc"),
        }
        for pkg in r.get("packaging", []):
            lookup[pkg["package_ndc"]] = fields
    return lookup


def main() -> None:
    all_csv = EPILLID_FOLDS_DIR / f"{FOLD_PREFIX}_all.csv"
    if not all_csv.exists():
        raise FileNotFoundError(f"{all_csv} missing — run scripts/download_epillid.py first")

    df = pd.read_csv(all_csv)
    df["package_ndc"] = df.pilltype_id.str.split("_").str[0]

    ndc_lookup = build_ndc_lookup()
    ndc_fields = df.package_ndc.map(ndc_lookup)
    for col in ("generic_name", "brand_name", "dosage_form", "product_ndc"):
        df[col] = ndc_fields.map(lambda d, c=col: d.get(c) if isinstance(d, dict) else None)

    # Pillbox appearance fields — not available yet (see module docstring).
    for col in ("imprint", "shape", "color", "size_mm", "score"):
        df[col] = None

    matched = df.generic_name.notna().sum()
    print(f"NDC join: {matched}/{len(df)} rows matched ({matched / len(df):.1%})")
    print(
        "  (expected to be low — most of ePillID's package NDCs have been delisted "
        "from the current NDC directory since; see module docstring)"
    )
    print(
        "appearance fields (imprint/shape/color/size/score): 0% populated — "
        "Pillbox metadata source not yet resolved (see data/manifests/pillbox.json)"
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "epillid_ndc_joined.csv"
    df.to_csv(out_path, index=False)
    print(f"wrote {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
