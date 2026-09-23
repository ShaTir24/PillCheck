# PillCheck ML

Dataset ingest, encoder training, and eval harness for pill recognition (PRD §14 Phases 0-1). See `CLAUDE.md` for scope and conventions.

## Setup

```
cd ml
uv sync
```

## Run

```
make download-data   # ePillID (~160MB) + NDC (~28MB) auto-download; c3pi/pillbox need a manual URL first
make build-splits    # join NDC metadata onto ePillID images, smoke-test, build our own train/val/test split registry
make eval-baseline   # embed ePillID's official test fold with a frozen pretrained model, report top-1/top-5
```

`make eval-baseline` took ~2m20s on a CPU-only M-series laptop for the full 9,804-image gallery + 745-query test fold (resnet18, no fine-tuning): **top-1 14.6%, top-5 34.4%**. That's a sanity-check number, not the paper's published SOTA (which requires their trained multi-head metric model) — see `eval/harness.py`'s docstring.

## Known gaps (documented, not silently skipped)

- `data/manifests/c3pi.json` and `pillbox.json` have no auto-resolvable download URL (C3PI/Pillbox are discontinued NLM datasets with no clean bulk-download API found). Resolve manually before `download_c3pi.py`/`download_pillbox.py` will run — see each manifest's `notes`.
- `join_metadata.py`'s NDC join match rate is near-zero for ePillID specifically: the live NDC directory only lists currently-marketed products, and ePillID's images are ~2016-2018 vintage. This is a real, measured finding, not a bug — see the script's docstring.

## Phase 1: training the encoder (Kaggle GPU)

No local GPU is assumed — training runs on a Kaggle GPU notebook; everything else (data, eval, index-building) runs locally as before.

```
uv run python train/encoder.py --limit 64 --batch-size 8 --epochs 1   # local CPU smoke test first
```

Then, on Kaggle:
1. Zip `scripts/`, `train/`, `eval/`, `configs/` (skip `data/`, `outputs/`, `.venv/`) and upload as a Kaggle Dataset.
2. Open `kaggle/train_encoder.ipynb` on Kaggle (GPU accelerator + internet on), attach that dataset as input, run it top to bottom.
3. Download the resulting `outputs/encoder/latest.pt` from the notebook's Output tab back into `ml/outputs/encoder/latest.pt` locally (gitignored — checkpoints don't belong in git).

Then, locally:
```
uv run python scripts/build_reference_index.py --checkpoint outputs/encoder/latest.pt
uv run python eval/harness.py --checkpoint outputs/encoder/latest.pt
```
Compare the printed top-1/top-5 against the Phase 0 baseline (14.6% / 34.4%) — see `DECISIONS.md` ADR-008 for the recorded result once a real training run has been done.

`convnext_tiny` is noticeably heavier than the `resnet18` baseline on CPU (~4s/batch-of-32 vs. ~0.4s) — the full 9,804-image gallery takes ~20min locally for `build_reference_index.py`/`eval/harness.py --checkpoint`. Use `--limit` on either script for a fast local smoke test; only run the full pass when you actually need the real number.

Not built yet (PRD Phase 1 items that don't need a GPU): OCR fusion, calibration/abstention, the Gradio demo.
