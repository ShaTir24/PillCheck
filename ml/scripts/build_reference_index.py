"""Build the reference index from a trained checkpoint: embed the full
reference gallery and save (embeddings, labels) for retrieval.

Not FAISS: verified during implementation that torch+faiss segfault
in-process on macOS ARM even with fully sequential (non-concurrent) use —
`import faiss` alone crashes once torch has been imported at all, before any
concurrent use. Plain numpy matmul is correct and fast enough at this scale
(9,804 vectors) — same approach as eval/metrics.py. A real approximate-search
index is a Phase 3 concern for the on-device export pipeline, not this
desktop dev step.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eval"))
from baseline import embed_images  # noqa: E402
from trained_encoder import load_trained_model  # noqa: E402

FOLDS_DIR = (
    Path(__file__).resolve().parent.parent
    / "data/raw/epillid/ePillID_data/folds/pilltypeid_nih_sidelbls0.01_metric_5folds/base"
)
IMG_ROOT = (
    Path(__file__).resolve().parent.parent / "data/raw/epillid/ePillID_data/classification_data"
)
FOLD_PREFIX = "pilltypeid_nih_sidelbls0.01_metric_5folds"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "index"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--limit", type=int, default=None, help="smoke-test subset size")
    args = parser.parse_args()

    all_df = pd.read_csv(FOLDS_DIR / f"{FOLD_PREFIX}_all.csv")
    gallery_df = all_df[all_df.is_ref].reset_index(drop=True)
    if args.limit:
        gallery_df = gallery_df.iloc[: args.limit]

    model, transform = load_trained_model(args.checkpoint)
    gallery_paths = [str(IMG_ROOT / p) for p in gallery_df.image_path]
    embeddings = embed_images(gallery_paths, model, transform)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    np.save(output_dir / "gallery_embeddings.npy", embeddings)
    np.save(output_dir / "gallery_labels.npy", gallery_df.pilltype_id.to_numpy())
    print(f"wrote {len(gallery_df)} reference embeddings to {output_dir}")


if __name__ == "__main__":
    main()
