"""Frozen, off-the-shelf embedding model — validates the eval harness, NOT the
production encoder. Phase 1 replaces this with an ArcFace-trained head
(PRD §12); no training happens here."""

import numpy as np
import timm
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


class ImageListDataset(Dataset):
    def __init__(self, paths: list, transform):
        self.paths = paths
        self.transform = transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int):
        img = Image.open(self.paths[idx]).convert("RGB")
        return self.transform(img)


def load_baseline_model(model_name: str = "resnet18"):
    model = timm.create_model(model_name, pretrained=True, num_classes=0)  # pooled features
    model.eval()
    config = timm.data.resolve_data_config({}, model=model)
    transform = timm.data.create_transform(**config)
    return model, transform


@torch.no_grad()
def embed_images(
    paths: list, model, transform, batch_size: int = 32, num_workers: int = 0
) -> np.ndarray:
    loader = DataLoader(
        ImageListDataset(paths, transform), batch_size=batch_size, num_workers=num_workers
    )
    all_embeddings = []
    for batch in tqdm(loader, desc="embedding"):
        features = model(batch)
        features = torch.nn.functional.normalize(features, dim=1)
        all_embeddings.append(features.numpy())
    return np.concatenate(all_embeddings, axis=0)
