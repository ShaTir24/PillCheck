"""Top-k retrieval accuracy: shared by the Phase 0 baseline harness and later phases.

Retrieval-based (query embedding -> nearest gallery embeddings), matching the
production architecture (PRD §10.1: ANN lookup vs. reference index) rather
than a softmax classifier — appropriate since low-shot pill ID has ~1
reference image per appearance class.

Plain numpy, not FAISS: at Phase 0's scale (thousands of vectors) an exact
brute-force matmul is fast enough and sidesteps a torch/faiss libomp conflict
that segfaults on macOS ARM. FAISS is worth it for the real on-device ANN
index (PRD §12) — revisit if a later phase's gallery grows past what a numpy
matmul handles comfortably.
"""

import numpy as np


def topk_accuracy(
    query_embeddings: np.ndarray,
    query_labels: np.ndarray,
    gallery_embeddings: np.ndarray,
    gallery_labels: np.ndarray,
    ks: tuple[int, ...] = (1, 5),
) -> dict[int, float]:
    """Embeddings must be L2-normalized; similarity = inner product (cosine)."""
    # Apple's Accelerate BLAS backend raises spurious FP warnings on this matmul on
    # arm64 (values are correct — verified against the same op without errstate).
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        similarity = query_embeddings @ gallery_embeddings.T  # (n_queries, n_gallery)

    max_k = min(max(ks), similarity.shape[1])
    top_indices = np.argpartition(-similarity, max_k - 1, axis=1)[:, :max_k]
    # re-sort just the top-k slice by actual similarity, descending
    row_idx = np.arange(similarity.shape[0])[:, None]
    order = np.argsort(-similarity[row_idx, top_indices], axis=1)
    top_indices = top_indices[row_idx, order]

    retrieved_labels = gallery_labels[top_indices]  # (n_queries, max_k)
    correct = retrieved_labels == query_labels[:, None]
    return {k: float(correct[:, :k].any(axis=1).mean()) for k in ks}
