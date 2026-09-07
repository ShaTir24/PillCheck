"""Download and extract the ePillID benchmark dataset (PRD §11.1).

License note: the repo is MIT, but its README states the dataset itself is
released "for research purposes only" — that's narrower than MIT. Confirm
this covers your intended use before bundling any of these images into a
shipped product; using it to reproduce the published baseline (Phase 0's
actual goal) is squarely research use.
"""


from _download_utils import RAW_DIR, download_file, load_manifest, unzip, verify_checksum


def main() -> None:
    manifest = load_manifest("epillid")
    zip_path = RAW_DIR / "epillid" / "ePillID_data.zip"
    download_file(manifest["download_url"], zip_path)
    verify_checksum(zip_path, manifest["sha256"])
    unzip(zip_path, RAW_DIR / "epillid")
    print(f"extracted to {RAW_DIR / 'epillid'}")


if __name__ == "__main__":
    main()
