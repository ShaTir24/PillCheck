"""Smoke check for join_metadata.py's output — not a full test suite (Phase 0
is a data pipeline; the eval harness result is the real pass/fail signal).
Run after join_metadata.py: `uv run python scripts/test_join.py`."""

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

MIN_EXPECTED_ROWS = 13000  # ePillID has ~13.5k rows; catches a truncated/broken read

# No hard floor on match rate: empirically ~0.5% of ePillID's package NDCs are
# still listed in the current NDC directory (most were delisted years ago —
# see join_metadata.py's docstring). A floor here would either be fake-strict
# or so low it catches nothing; the real regression to guard against is the
# join key extraction silently breaking, which zero-rows-with-package_ndc
# would indicate regardless of how many actually resolve.


def main() -> None:
    path = PROCESSED_DIR / "epillid_ndc_joined.csv"
    df = pd.read_csv(path)

    assert len(df) >= MIN_EXPECTED_ROWS, f"expected >={MIN_EXPECTED_ROWS} rows, got {len(df)}"
    assert df.package_ndc.notna().all(), "package_ndc extraction produced nulls — check pilltype_id"

    match_rate = df.generic_name.notna().mean()
    print(f"OK: {len(df)} rows, {match_rate:.1%} NDC match rate (low rate is expected, see notes)")


if __name__ == "__main__":
    main()
