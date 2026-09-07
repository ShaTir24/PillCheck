"""PyTorch Dataset over ePillID's own fold CSVs for ArcFace encoder training.

Train set = all reference images (is_ref==True) + consumer images in folds
0-3. Fold 4 is deliberately excluded — it's the same held-out test set
eval/harness.py scores the baseline (and this trained encoder) against, so
the before/after comparison stays apples-to-apples.

Label = pilltype_id + side (the paper's "appearance class", 9804-way) — not
pilltype_id alone (4902-way) — gives the encoder more separating signal per
class. eval/harness.py still evaluates at the pilltype_id level, which is
the level that matters for the product's MATCH decision.
"""

from pathlib import Path

import pandas as pd
import timm
from PIL import Image
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset

EPILLID_ROOT = Path(__file__).resolve().parent.parent / "data/raw/epillid/ePillID_data"
FOLDS_DIR = EPILLID_ROOT / "folds/pilltypeid_nih_sidelbls0.01_metric_5folds/base"
IMG_ROOT = EPILLID_ROOT / "classification_data"
FOLD_PREFIX = "pilltypeid_nih_sidelbls0.01_metric_5folds"
HELDOUT_TEST_FOLD = 4  # matches eval/harness.py's default --test-fold


def load_train_df() -> pd.DataFrame:
    all_df = pd.read_csv(FOLDS_DIR / f"{FOLD_PREFIX}_all.csv")
    train_fold_ids = [i for i in range(5) if i != HELDOUT_TEST_FOLD]
    train_consumer_paths = set()
    for fold_id in train_fold_ids:
        fold_df = pd.read_csv(FOLDS_DIR / f"{FOLD_PREFIX}_{fold_id}.csv")
        train_consumer_paths.update(fold_df.image_path)

    is_train_consumer = (~all_df.is_ref) & all_df.image_path.isin(train_consumer_paths)
    df = all_df[all_df.is_ref | is_train_consumer].reset_index(drop=True)
    df["appearance_class"] = df.pilltype_id + "_" + df.is_front.astype(str)
    return df


class EPillIDTrainDataset(Dataset):
    def __init__(self, df: pd.DataFrame, label_encoder: LabelEncoder, transform):
        self.df = df
        self.label_encoder = label_encoder
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        img = Image.open(IMG_ROOT / row.image_path).convert("RGB")
        label = self.label_encoder.transform([row.appearance_class])[0]
        return self.transform(img), label


def build_train_dataset(backbone: str) -> tuple[EPillIDTrainDataset, LabelEncoder]:
    df = load_train_df()
    label_encoder = LabelEncoder().fit(df.appearance_class)

    model = timm.create_model(backbone, pretrained=True, num_classes=0)
    config = timm.data.resolve_data_config({}, model=model)
    # hflip=0 — imprint text orientation is meaningful, unlike most vision tasks
    transform = timm.data.create_transform(**config, is_training=True, hflip=0.0)

    return EPillIDTrainDataset(df, label_encoder, transform), label_encoder
