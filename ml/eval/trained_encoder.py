"""Loads a trained ArcFace checkpoint into the same (model, transform) shape
eval/baseline.py returns, so eval/harness.py can embed with either without
caring which one it got."""

import sys
from pathlib import Path

import timm
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "train"))
from encoder import Encoder  # noqa: E402


def load_trained_model(checkpoint_path: str):
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    model = Encoder(ckpt["backbone"], ckpt["embedding_dim"])
    model.load_state_dict(ckpt["encoder_state"])
    model.eval()

    config = timm.data.resolve_data_config({}, model=model.backbone)
    transform = timm.data.create_transform(**config)
    return model, transform
