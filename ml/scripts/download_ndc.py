"""Download the FDA NDC directory (imprint/shape/color/size metadata, PRD §11.1).

Resolves the current export URL from openFDA's own download.json metadata
endpoint at run time rather than hardcoding it — openFDA repartitions these
exports periodically, so a hardcoded URL goes stale silently.
"""

from pathlib import Path

import requests
from _download_utils import RAW_DIR, download_file, load_manifest, unzip, verify_checksum


def resolve_download_url(metadata_url: str, path: list) -> str:
    data = requests.get(metadata_url, timeout=30).json()
    node = data
    for key in path:
        node = node[key]
    return node


def main() -> None:
    manifest = load_manifest("ndc")
    url = resolve_download_url(manifest["metadata_url"], manifest["metadata_path"])
    print(f"resolved current NDC export: {url}")

    zip_path = RAW_DIR / "ndc" / Path(url).name
    download_file(url, zip_path)
    verify_checksum(zip_path, manifest["sha256"])
    unzip(zip_path, RAW_DIR / "ndc")
    print(f"extracted to {RAW_DIR / 'ndc'}")


if __name__ == "__main__":
    main()
