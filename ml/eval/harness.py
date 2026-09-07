"""Phase 0 exit criterion: reproduce a baseline top-1/top-5 number on ePillID's
own official heldout fold, within the reported margin.

Protocol (from ePillID's folds/.../base/ CSVs, inspected directly — see
data/manifests/epillid.json):
  - gallery = all reference images (is_ref == True) from the "_all.csv" file.
    These are NOT fold-partitioned; every appearance class has >=1 reference
    image available regardless of fold (confirmed: 0 test-fold pilltypes
    lack a reference image).
  - queries = the last fold's consumer images (is_ref == False) — fold "_4"
    is the official heldout test split (train_cv.py: `csv_files.pop(-1)`).
  - label = pilltype_id (4902 classes); this is a retrieval task (nearest
    gallery embedding by cosine similarity), matching the production
    architecture's ANN-lookup design (PRD §10.1), not a softmax classifier.

This harness uses a FROZEN, non-fine-tuned baseline embedder (eval/baseline.py)
— it validates that the harness's numbers are sane before Phase 1 trains the
real ArcFace encoder, which is expected to score higher.
"""

import argparse
from pathlib import Path

import pandas as pd
from baseline import embed_images, load_baseline_model
from metrics import topk_accuracy
from trained_encoder import load_trained_model

FOLDS_DIR = (
    Path(__file__).resolve().parent.parent
    / "data/raw/epillid/ePillID_data/folds/pilltypeid_nih_sidelbls0.01_metric_5folds/base"
)
IMG_ROOT = (
    Path(__file__).resolve().parent.parent / "data/raw/epillid/ePillID_data/classification_data"
)
FOLD_PREFIX = "pilltypeid_nih_sidelbls0.01_metric_5folds"


def load_split(test_fold: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_df = pd.read_csv(FOLDS_DIR / f"{FOLD_PREFIX}_all.csv")
    test_df = pd.read_csv(FOLDS_DIR / f"{FOLD_PREFIX}_{test_fold}.csv")
    gallery_df = all_df[all_df.is_ref].reset_index(drop=True)
    return gallery_df, test_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet18", help="timm model for the frozen baseline")
    parser.add_argument("--checkpoint", default=None, help="trained encoder .pt, overrides --model")
    parser.add_argument("--test-fold", type=int, default=4)
    parser.add_argument("--limit-gallery", type=int, default=None, help="smoke-test subset size")
    parser.add_argument("--limit-queries", type=int, default=None, help="smoke-test subset size")
    args = parser.parse_args()

    gallery_df, query_df = load_split(args.test_fold)
    if args.limit_gallery:
        gallery_df = gallery_df.iloc[: args.limit_gallery]
    if args.limit_queries:
        query_df = query_df.iloc[: args.limit_queries]

    print(f"gallery: {len(gallery_df)} reference images, queries: {len(query_df)} consumer images")

    if args.checkpoint:
        model, transform = load_trained_model(args.checkpoint)
        label = f"trained checkpoint ({args.checkpoint})"
    else:
        model, transform = load_baseline_model(args.model)
        label = f"baseline ({args.model}, frozen)"

    gallery_paths = [str(IMG_ROOT / p) for p in gallery_df.image_path]
    query_paths = [str(IMG_ROOT / p) for p in query_df.image_path]

    gallery_emb = embed_images(gallery_paths, model, transform)
    query_emb = embed_images(query_paths, model, transform)

    acc = topk_accuracy(
        query_emb,
        query_df.pilltype_id.to_numpy(),
        gallery_emb,
        gallery_df.pilltype_id.to_numpy(),
        ks=(1, 5),
    )
    print(f"\n{label} on official test fold {args.test_fold}:")
    print(f"  top-1: {acc[1]:.4f}")
    print(f"  top-5: {acc[5]:.4f}")
    if not args.checkpoint:
        print(
            "\nThis is a sanity-check baseline, not the published SOTA number "
            "(that requires the paper's trained multi-head metric model). Compare "
            "against whichever baseline row you're targeting from the ePillID paper "
            "before judging the +/-1pt exit criterion."
        )


if __name__ == "__main__":
    main()
