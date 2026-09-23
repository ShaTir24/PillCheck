"""Shared helpers for the download_*.py scripts. Not a script itself."""

import hashlib
import json
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

MANIFEST_DIR = Path(__file__).resolve().parent.parent / "data" / "manifests"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_manifest(name: str) -> dict:
    return json.loads((MANIFEST_DIR / f"{name}.json").read_text())


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"already downloaded: {dest}")
        return dest
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    tmp = dest.with_suffix(dest.suffix + ".part")
    with open(tmp, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
            bar.update(len(chunk))
    tmp.rename(dest)
    return dest


def verify_checksum(path: Path, expected_sha256: str | None) -> None:
    actual = sha256_of(path)
    if expected_sha256 is None:
        print(f"no pinned checksum for {path.name} yet — computed sha256: {actual}")
        print("pin it in the manifest to make future downloads verifiable.")
        return
    if actual != expected_sha256:
        raise ValueError(f"checksum mismatch for {path}: expected {expected_sha256}, got {actual}")
    print(f"checksum OK: {path.name}")


def unzip(zip_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
