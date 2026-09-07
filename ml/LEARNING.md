# Learning Guide — Before You Train on Kaggle

A study path for the concepts behind `ml/train/encoder.py`, `ml/eval/harness.py`, and `kaggle/train_encoder.ipynb`. Topics are ordered to match the sequence you'll actually work through: environment first, then the data/problem framing, then the model, then how it trains, then how it's judged. Each section says what it means for *our* code specifically, then links out for depth.

You don't need to master every linked resource before starting — skim the "what this means for us" text in each section first; come back to a video/article when something in the notebook doesn't make sense.

---

## 1. Kaggle Notebooks & GPU Environments

**Why it's first:** you'll be running `kaggle/train_encoder.ipynb` on Kaggle's infrastructure, not your laptop. You need to know what `/kaggle/input` vs `/kaggle/working` means, why sessions have a time limit, and how to turn on the GPU + internet — before opening the notebook, not while debugging it.

**What this means for us:** our notebook copies the uploaded `ml/` code from the read-only `/kaggle/input` into the writable `/kaggle/working` as its first cell — that's not boilerplate, it's working around exactly this input/output split. The ~9-hour session cap is why `encoder.py` checkpoints every epoch and supports `--resume-from`.

- Video: [How to Use Kaggle Notebook | Accessing GPU | Beginner Guide](https://www.youtube.com/watch?v=Z-rmmlhBJ3c)
- Article: [Kaggle Datasets & Notebooks Tutorial (DataCamp)](https://www.datacamp.com/tutorial/tutorial-kaggle-datasets-tutorials-kaggle-notebooks)

---

## 2. The Actual Problem: Low-Shot, Fine-Grained Recognition

**Why it's next:** before the model/code makes sense, it helps to know *why* this isn't a normal "cat vs. dog" classifier. ePillID has ~4,902 pill types with often exactly **one** reference photo per type — that's "low-shot." And two different pills can look nearly identical — that's "fine-grained." Both facts shape every decision downstream (why we don't train a plain softmax classifier, why retrieval/embeddings are used instead, why augmentation matters more here than usual).

**What this means for us:** `ml/train/dataset.py`'s docstring and `ml/eval/harness.py`'s docstring both explain this directly — re-read them after this section, they'll make more sense.

- Article: [ePillID paper (arXiv) — read at least the abstract and Figure 1](https://arxiv.org/abs/2005.14288)
- Article (context on why retrieval, not classification, is standard here): [How to use metric learning: embedding is all you need](https://medium.com/data-science/how-to-use-metric-learning-embedding-is-all-you-need-f26e01597375)

---

## 3. Transfer Learning & Pretrained CNN Backbones

**Why it's next:** `encoder.py` doesn't train a CNN from scratch — it starts from `timm.create_model("convnext_tiny", pretrained=True, ...)`, a model already trained on ImageNet. Understanding *why* that's the right starting point (and what "freezing" vs. "fine-tuning" means, even though we fine-tune the whole thing here) is foundational before the ArcFace-specific material.

**What this means for us:** `Encoder.__init__` in `ml/train/encoder.py` loads a pretrained ConvNeXt-Tiny and adds a small linear "embedding head" on top. We fine-tune the *entire* network (not just the head) with a small learning rate (`1e-4` in `configs/encoder.yaml`) — a real GPU is what makes fine-tuning the whole backbone practical instead of only the head.

- Video: [PyTorch Tutorial 15 - Transfer Learning](https://www.youtube.com/watch?v=K0lWSB2QoIQ)
- Article: [Transfer Learning for Computer Vision Tutorial (official PyTorch docs)](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

---

## 4. ConvNeXt: the Specific Backbone We Use

**Why it's next:** now that "pretrained CNN backbone" makes sense generally, it's worth 15 minutes on *this specific* architecture — ConvNeXt is a 2022 design that modernized plain CNNs using ideas borrowed from Vision Transformers, and out-performs many ViTs while staying a normal convolutional network (simpler to export to mobile later, per the PRD's on-device requirement).

**What this means for us:** `--backbone convnext_tiny` is a single string passed to `timm` — you don't need to hand-build this architecture, just understand roughly what it's doing when you see it in a loss curve or a paper comparison table.

- Video: [ConvNeXt: A ConvNet for the 2020s – Paper Explained (with animations)](https://www.youtube.com/watch?v=QqejV0LNDHA)
- Article: [ConvNeXt model architecture (OpenGenus)](https://iq.opengenus.org/convnext-model/)

---

## 5. Data Augmentation for Images

**Why it's next:** `dataset.py` builds its training transform via `timm.data.create_transform(..., is_training=True, hflip=0.0)`. Before that line makes sense, it helps to know what augmentation is *for* (fighting overfitting on a low-shot dataset) and why we deliberately turned **off** horizontal flipping.

**What this means for us:** most vision tasks flip images to double their data for free. We can't — pill imprints are text, and flipped text is wrong text. This is a good example of "don't blindly apply defaults" that's worth internalizing before you tweak any augmentation settings yourself.

- Video: [Data Augmentation Techniques | Deep learning tutorial](https://www.youtube.com/watch?v=F8uFAkHfK18)
- Article: [A Complete Guide to Data Augmentation (DataCamp)](https://www.datacamp.com/tutorial/complete-guide-data-augmentation)

---

## 6. PyTorch Training Mechanics: Dataset, DataLoader, Training Loop

**Why it's next:** this is the "plumbing" — how images actually flow from disk into the model and how the model's weights actually get updated. If you've never read a PyTorch training loop line-by-line before, do this section before opening `encoder.py`'s `main()` function.

**What this means for us:** `ml/train/dataset.py`'s `EPillIDTrainDataset` is a standard PyTorch `Dataset` (implements `__len__`/`__getitem__`); `encoder.py`'s `main()` has the standard loop shape: `for images, labels in loader: forward → loss → zero_grad → backward → step`. The only non-standard part is what "loss" actually is here — that's Topics 7-8.

- Article: [Datasets & DataLoaders (official PyTorch tutorial)](https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html)
- Video: [Understanding the PyTorch Training Loop | Forward, Loss, Backprop Explained](https://www.youtube.com/watch?v=w_L0o3bRD1k)

---

## 7. Metric Learning & Embedding Spaces

**Why it's next:** this is the conceptual shift from "normal" deep learning classifiers. Instead of the model outputting "this is pill class #4218," it outputs a vector (an *embedding*) — and the training goal is to arrange those vectors in space so the same pill's photos cluster together and different pills stay far apart. This is what makes low-shot recognition (Topic 2) actually work: you can add a brand-new pill later just by embedding one photo of it, no retraining required.

**What this means for us:** `Encoder.forward()` ends with `torch.nn.functional.normalize(embedding, dim=1)` — every embedding gets projected onto a unit sphere, because what matters is the *direction* of the vector (angle between pills), not its length. That's the setup ArcFace (next section) builds directly on.

- Video: [Machine Learning Crash Course: Embeddings (Google)](https://www.youtube.com/watch?v=my5wFNQpFO0)
- Article: [How to use metric learning: embedding is all you need](https://medium.com/data-science/how-to-use-metric-learning-embedding-is-all-you-need-f26e01597375)

---

## 8. ArcFace: the Loss Function That Actually Does the Work

**Why it's next:** this is the single most important — and least obvious — piece of `encoder.py`. `ArcFaceLoss` (from `pytorch-metric-learning`) is what turns "normalized embeddings + class labels" into a training signal that pulls same-pill embeddings together and pushes different-pill embeddings apart, with an explicit angular *margin* enforcing a safety gap between classes.

**What this means for us:** `arcface = ArcFaceLoss(num_classes, args.embedding_dim)` in `encoder.py` is doing all of the actual "make the embeddings good" work — the backbone (ConvNeXt) just produces the raw features it operates on. This is originally a face-recognition technique (same low-shot, fine-grained shape as pill ID: many identities, few photos each), which is exactly why it transfers well here.

- Video: [ArcFace Explained: State-of-the-Art Face Recognition with Angular Margin](https://www.youtube.com/watch?v=66jO7fdUELk)
- Article: [Face Recognition with ArcFace (LearnOpenCV)](https://learnopencv.com/face-recognition-with-arcface/)
- Primary source (skim, don't need to fully derive the math): [ArcFace: Additive Angular Margin Loss for Deep Face Recognition (arXiv)](https://arxiv.org/abs/1801.07698)

---

## 9. Evaluating a Retrieval Model: Cosine Similarity & Top-k Accuracy

**Why it's next:** once training produces embeddings, "is this model good?" isn't measured with normal classification accuracy — it's measured by retrieval: given a query pill photo, does the *correct* reference photo show up in the nearest few matches?

**What this means for us:** `ml/eval/metrics.py`'s `topk_accuracy` does exactly this: `query_embeddings @ gallery_embeddings.T` computes cosine similarity between every query and every reference (because both are unit vectors, dot product = cosine of the angle between them — this is the same "angle" ArcFace was optimizing in Topic 8). Top-1/top-5 then just check whether the correct pill type is the closest match, or within the closest five.

- Video: [Cosine Distance & Cosine Similarity | K Nearest Neighbors](https://www.youtube.com/watch?v=61MFz12zlgQ)
- Article: [Retrieval Techniques: Cosine Similarity and kNN](https://www.educative.io/courses/llm-bootcamp/retrieval-techniques-cosine-similarity-and-knn)

---

## 10. Looking Ahead: Vector Search at Scale (FAISS)

**Why it's last:** not used in our current code (see ADR-008 — FAISS segfaults against torch on this machine, so `scripts/build_reference_index.py` uses plain numpy instead) but worth understanding conceptually, since PRD §12 calls for a real approximate-nearest-neighbor index on-device eventually, once the reference library is larger than a few thousand pills.

**What this means for us:** everything in Topic 9 *is* what FAISS does internally, just unoptimized — `IndexFlatIP` is the exact brute-force version of our numpy matmul. FAISS matters once the gallery is too large for brute-force search to stay fast, not before.

- Video: [Understanding FAISS for efficient similarity search of dense vectors](https://www.youtube.com/watch?v=0jOlZpFFxCE)
- Article: [Introduction to Facebook AI Similarity Search (Faiss) — Pinecone](https://www.pinecone.io/learn/series/faiss/faiss-tutorial/)

---

## Quick cross-reference

| Topic | Code it explains |
|---|---|
| 1. Kaggle | `kaggle/train_encoder.ipynb` |
| 2. Low-shot/fine-grained framing | `ml/train/dataset.py`, `ml/eval/harness.py` docstrings |
| 3-4. Transfer learning / ConvNeXt | `Encoder.__init__` in `ml/train/encoder.py` |
| 5. Augmentation | `build_train_dataset` in `ml/train/dataset.py` |
| 6. Training mechanics | `main()` loop in `ml/train/encoder.py` |
| 7-8. Metric learning / ArcFace | `Encoder.forward()`, `ArcFaceLoss` usage in `ml/train/encoder.py` |
| 9. Retrieval evaluation | `ml/eval/metrics.py`, `ml/eval/harness.py` |
| 10. Vector search at scale | `ml/scripts/build_reference_index.py`, ADR-008 |
