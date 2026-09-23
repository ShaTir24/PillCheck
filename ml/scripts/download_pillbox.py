"""Download the archived Pillbox image library (imprint/shape/color source, PRD §11.1).

Pillbox was retired in 2021; only its final image zip has a confirmed bulk
URL. The structured per-pill metadata (SPLIMPRINT/SPLSHAPE/SPLCOLOR/SPLSIZE/
SPLSCORE) doesn't have a confirmed bulk-download source — see
data/manifests/pillbox.json. This script only fetches the images; it does
not fabricate a metadata download.
"""

from pathlib import Path

from _download_utils import RAW_DIR, download_file, load_manifest, unzip, verify_checksum


def main() -> None:
    manifest = load_manifest("pillbox")
    zip_path = RAW_DIR / "pillbox" / Path(manifest["images_url"]).name
    download_file(manifest["images_url"], zip_path)
    verify_checksum(zip_path, manifest["sha256"])
    unzip(zip_path, RAW_DIR / "pillbox" / "images")
    print(f"extracted images to {RAW_DIR / 'pillbox' / 'images'}")

    if not manifest.get("metadata_download_url"):
        print(
            "\nNOTE: pillbox.json has no metadata_download_url — imprint/shape/color/size "
            "fields are NOT available yet. Resolve that source manually before running "
            "join_metadata.py if you need those fields (see pillbox.json's notes)."
        )


if __name__ == "__main__":
    main()
