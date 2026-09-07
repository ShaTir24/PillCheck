"""Download the NLM C3PI reference images (reference-library seed, PRD §11.1).

Unlike ePillID/NDC, no API-exposed direct asset URL could be found for this
dataset (data.gov/healthdata.gov's Socrata API returns no attachment
metadata for it, and C3PI was discontinued in 2018). Refuses to guess a URL.
"""

import sys
from pathlib import Path

from _download_utils import RAW_DIR, download_file, load_manifest, unzip, verify_checksum


def main() -> None:
    manifest = load_manifest("c3pi")
    if not manifest.get("download_url"):
        print(
            "c3pi.json has no download_url. Resolve the current direct link for the "
            "~6.8GB reference-images zip from:\n"
            f"  {manifest['source']}\n"
            "then fill in download_url (and sha256, once downloaded) in "
            "data/manifests/c3pi.json before re-running this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    zip_path = RAW_DIR / "c3pi" / Path(manifest["download_url"]).name
    download_file(manifest["download_url"], zip_path)
    verify_checksum(zip_path, manifest["sha256"])
    unzip(zip_path, RAW_DIR / "c3pi")
    print(f"extracted to {RAW_DIR / 'c3pi'}")


if __name__ == "__main__":
    main()
