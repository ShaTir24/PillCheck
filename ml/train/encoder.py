"""ArcFace metric-learning encoder training (PRD §12).

Checkpointed every epoch and resumable (--resume-from) — Kaggle GPU sessions
cap at ~9h, so a run that outlives one session continues in the next instead
of restarting. Run this from a WRITABLE copy of ml/ (Kaggle's /kaggle/input
is read-only — see kaggle/train_encoder.ipynb, which copies ml/ to
/kaggle/working before running anything).
"""

import argparse
from pathlib import Path

import timm
import torch
import yaml
from dataset import build_train_dataset
from pytorch_metric_learning.losses import ArcFaceLoss
from torch.utils.data import DataLoader
from tqdm import tqdm

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "encoder"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "encoder.yaml"


def load_defaults() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


class Encoder(torch.nn.Module):
    def __init__(self, backbone: str, embedding_dim: int):
        super().__init__()
        self.backbone = timm.create_model(backbone, pretrained=True, num_classes=0)
        self.embed = torch.nn.Linear(self.backbone.num_features, embedding_dim)

    def forward(self, x):
        features = self.backbone(x)
        embedding = self.embed(features)
        return torch.nn.functional.normalize(embedding, dim=1)


def save_checkpoint(
    path: Path, epoch: int, encoder: Encoder, arcface: ArcFaceLoss, optimizer, args
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "encoder_state": encoder.state_dict(),
            "arcface_state": arcface.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "backbone": args.backbone,
            "embedding_dim": args.embedding_dim,
        },
        path,
    )


def main() -> None:
    defaults = load_defaults()
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", default=defaults["backbone"])
    parser.add_argument("--embedding-dim", type=int, default=defaults["embedding_dim"])
    parser.add_argument("--batch-size", type=int, default=defaults["batch_size"])
    parser.add_argument("--lr", type=float, default=defaults["lr"])
    parser.add_argument("--epochs", type=int, default=defaults["epochs"])
    parser.add_argument("--seed", type=int, default=defaults["seed"])
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--resume-from", default=None)
    parser.add_argument("--limit", type=int, default=None, help="smoke-test subset size")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_dataset, label_encoder = build_train_dataset(args.backbone)
    if args.limit:
        train_dataset.df = train_dataset.df.iloc[: args.limit].reset_index(drop=True)
    num_classes = len(label_encoder.classes_)
    loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)

    encoder = Encoder(args.backbone, args.embedding_dim).to(device)
    arcface = ArcFaceLoss(num_classes, args.embedding_dim).to(device)
    optimizer = torch.optim.Adam(
        list(encoder.parameters()) + list(arcface.parameters()), lr=args.lr
    )

    start_epoch = 0
    if args.resume_from:
        ckpt = torch.load(args.resume_from, map_location=device)
        encoder.load_state_dict(ckpt["encoder_state"])
        arcface.load_state_dict(ckpt["arcface_state"])
        optimizer.load_state_dict(ckpt["optimizer_state"])
        start_epoch = ckpt["epoch"] + 1
        print(f"resumed from {args.resume_from} at epoch {start_epoch}")

    output_dir = Path(args.output_dir)
    for epoch in range(start_epoch, args.epochs):
        encoder.train()
        total_loss = 0.0
        for images, labels in tqdm(loader, desc=f"epoch {epoch}"):
            images, labels = images.to(device), labels.to(device)
            embeddings = encoder(images)
            loss = arcface(embeddings, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"epoch {epoch}: avg loss {total_loss / len(loader):.4f}")
        save_checkpoint(output_dir / "latest.pt", epoch, encoder, arcface, optimizer, args)

    print(f"training done — checkpoint at {output_dir / 'latest.pt'}")


if __name__ == "__main__":
    main()
