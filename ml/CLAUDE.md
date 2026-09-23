# PillCheck ml — conventions

Dataset ingest, encoder training, and eval pipeline for pill recognition. Rationale: [`../DECISIONS.md`](../DECISIONS.md) ADR-007, ADR-008.

## Scope discipline

Phase 0 (data ingest + eval harness) and Phase 1's GPU-critical path (encoder training + reference index) are built. No detector/OCR/segmentation code, no Gradio demo — those are Phase 1's non-GPU items and Phase 2, and get their own directories when those phases start. Don't add them speculatively.

## Conventions

- **`uv`-managed**, separate env from `backend/` — heavy CV/ML deps don't belong in the FastAPI service.
- **No DVC.** `data/manifests/*.json` pins source URLs + sha256 + license notes; `data/raw/` and `data/processed/` are gitignored and rebuilt by scripts. If datasets start mutating or need cross-machine sharing, that's when DVC earns its keep — not before.
- **Never guess a dataset URL.** If a source has no clean API/bulk-download endpoint (see `data/manifests/c3pi.json`, `pillbox.json`), the download script refuses to run and prints where to resolve it manually — it does not fabricate a link.
- **Retrieval, not classification**, for eval metrics (`eval/metrics.py`): pill ID is low-shot (~1 reference image per class), so top-k is measured by nearest-embedding retrieval against a reference gallery — matching the production architecture's ANN lookup (PRD §10.1), not a softmax classifier.
- **Plain numpy over FAISS**, everywhere in this pipeline — `import faiss` alone segfaults (OMP Error #15) once torch has been imported in the same process, confirmed even with fully sequential (non-concurrent) use, not just concurrent access. Numpy is plenty fast at this scale (~10k vectors). A real approximate-search index is a Phase 3 on-device-export concern, not this desktop pipeline's.
- **GPU training runs on Kaggle**, not locally (ADR-008) — no local GPU confirmed available. `train/encoder.py` is written to run identically on a CPU smoke-test subset (`--limit`) and on Kaggle's GPU (full run); it doesn't special-case either environment. Checkpoints every epoch and supports `--resume-from` since Kaggle GPU sessions cap at ~9h.
- Kaggle's `/kaggle/input` is read-only — `kaggle/train_encoder.ipynb` copies the uploaded `ml/` code to `/kaggle/working` before running anything, so no script needs Kaggle-specific path handling.
- Run `uv run ruff check scripts eval train` before considering a change done.

## Known data gaps (don't silently "fix" these — they're documented findings)

- Pillbox is the source of imprint/shape/color/size fields (SPLIMPRINT etc.) — these are **not** in the openFDA NDC directory (confirmed by inspecting a live record). Pillbox's own bulk metadata download isn't resolved yet; `join_metadata.py` leaves those columns null rather than guessing.
- The live NDC directory's join match rate against ePillID's images is near-zero (~0.5%, measured) because ePillID's images are ~2016-2018 vintage and most of those exact package NDCs have since been delisted. The join is still correct — it just can't backfill historical images. Don't loosen this by joining on a fuzzier key to force a higher match rate; a low, honest number is correct here.
