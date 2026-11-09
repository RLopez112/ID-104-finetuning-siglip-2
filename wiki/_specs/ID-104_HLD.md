---
type: High-Level Design
title: "High-Level Design: ID-104 Local USD Multimodal Search Engine"
description: "High-level architecture, module decomposition, and data flow for a 100% local, offline-capable USD 3D asset retrieval system using SigLIP 2 and embedded Qdrant."
tags: [sdlc, hld, architecture, local-first, siglip2, qdrant, openusd]
status: approved
generated:
  by: spec-first-sdlc
  at: "2026-11-08T19:48:00-03:00"
---

# High-Level Design: ID-104 Local USD Multimodal Search Engine

**Version:** 1.0  
**Date:** 2026-11-08  
**Status:** Approved  
**Governing Intent:** `wiki/_specs/ID-104_Intent.md`  
**Governing ADRs:** `wiki/_specs/ID-104_ADR.md` (ADR-001, ADR-002, ADR-003, ADR-004)
**Gap Analysis Reference:** `wiki/_artifacts/ID-104_GapAnalysisReport.md`

---

## 1. Overview
The **ID-104 Local USD Multimodal Search Engine** provides artists, developers, and engineers with an offline, local-first indexing and retrieval tool for 3D OpenUSD asset libraries (`D:\___tmp\USD_assets`). By pairing local **SigLIP 2** vision-language embeddings with an **embedded Qdrant** vector store, the system enables sub-second text-to-3D and image-to-3D similarity searches directly from the desktop with zero external cloud dependencies.

---

## 2. Goals and Non-Goals

### Goals
- **100% Local Execution**: Ingestion, vector storage, model inference, and search querying must run strictly on local workstation hardware (GPU/CPU) without cloud calls.
- **Dual Query Modalities**: Support natural language text queries (e.g., "curved conference table", "high voltage transformer") and reference image queries (drag-and-drop or local file path).
- **Exact & Near-Neighbor Matching**: Return similarity scores and calibrated confidence thresholds to distinguish exact matches from semantically similar variations.
- **Embedded Zero-Config Storage**: Embed Qdrant directly into local directory storage (`50_PROJECT/data/qdrant_db/`) without requiring Docker or network port setups.
- **Lightweight Multimodal Interfaces**: Deliver an intuitive CLI for scripting/automation and an interactive localhost Web UI (Streamlit or Gradio) displaying asset thumbnails, categories, and direct USD file links.

### Non-Goals
- Real-time physics simulation or in-app USD stage authoring/editing (focused strictly on search & retrieval).
- Remote multi-user cloud SaaS deployment (this iteration is strictly a single-workstation local tool).
- Full 3D generative asset modeling (retrieval-only, not generative 3D).

---

## 3. System Architecture

### Component Diagram

```
+-----------------------------------------------------------------------------------+
|                            USER INTERFACE LAYER                                   |
|   +------------------------------------+   +----------------------------------+   |
|   |   Local Web UI (Streamlit/Gradio)  |   |        CLI Search Runner         |   |
|   |  - Text prompt / Image drop zone   |   |   - Command-line arguments       |   |
|   |  - Visual grid of results          |   |   - JSON/table output            |   |
|   +-----------------+------------------+   +-----------------+----------------+   |
+---------------------|----------------------------------------|--------------------+
                      |                                        |
                      +-------------------+--------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        APPLICATION & ENGINE CORE LAYER                            |
|   +------------------------------------+   +----------------------------------+   |
|   |           Search Engine            |   |          Asset Scanner           |   |
|   |  - Query dispatch (Text/Image)     |   |  - Traverses D:\___tmp\USD_assets|   |
|   |  - Thresholding & ranking          |   |  - Resolves .thumbs/ & metadata  |   |
|   +-----------------+------------------+   +-----------------+----------------+   |
|                     |                                        |                    |
|                     v                                        v                    |
|   +---------------------------------------------------------------------------+   |
|   |                        SigLIP 2 Model Service                             |   |
|   |  - PyTorch local weights (google/siglip2-base-patch16-224)                |   |
|   |  - encode_text(prompt) -> 768d vector                                     |   |
|   |  - encode_image(PIL.Image) -> 768d vector                                 |   |
|   |  - Device management (CUDA GPU / CPU fallback)                            |   |
|   +-------------------------------------+-------------------------------------+   |
+-----------------------------------------|-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         LOCAL PERSISTENCE LAYER                                   |
|   +---------------------------------------------------------------------------+   |
|   |                     Embedded Qdrant Client                                |   |
|   |  - Local disk path: 50_PROJECT/data/qdrant_db/                            |   |
|   |  - Collection: "usd_assets_siglip2"                                       |   |
|   |  - Distance metric: Cosine                                                |   |
|   |  - Payload: {usd_path, thumb_path, category, subcategory, filesize}       |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
```

### Component Descriptions

| Component | Responsibility | Key Interfaces |
|-----------|----------------|----------------|
| **`AssetScanner`** | Traverses target USD directory (`D:\___tmp\USD_assets`), identifies USD files, pairs them with thumbnails (`.thumbs/256x256/`), and extracts metadata. | `scan_assets(root_path) -> List[USDAssetMeta]` |
| **`SigLIP2Service`** | Loads local SigLIP 2 model and processor; computes normalized embeddings for text and images. | `encode_text(str) -> np.ndarray`<br>`encode_image(Image) -> np.ndarray` |
| **`VectorStore`** | Manages local embedded Qdrant database, collection lifecycle, vector upserts, and cosine similarity queries with payload filters. | `index_assets(List[AssetEmbedding])`<br>`search(vector, top_k, filter) -> List[SearchResult]` |
| **`SearchEngine`** | Coordinates querying logic, normalizes query inputs, sets exact-match vs similar thresholds, and formats response cards. | `query_by_text(query, top_k, category)`<br>`query_by_image(image_path, top_k, category)` |
| **`WebUI / CLI`** | Presents interactive user interface (Streamlit localhost) and terminal CLI commands for indexing and querying. | Streamlit App (`app.py`), CLI (`cli.py`) |

---

## 4. Data Flow

### 4.1 Indexing Workflow
1. User or setup script triggers `python cli.py index --target "D:\___tmp\USD_assets"`.
2. `AssetScanner` walks the filesystem and discovers all `.usd`, `.usda`, and `.usdc` files.
3. For each asset, `AssetScanner` resolves its preview thumbnail (e.g., `Boat.usd.auto.png`).
4. `SigLIP2Service` processes thumbnails in batches on local GPU/CPU, outputting normalized 768d feature vectors.
5. `VectorStore` upserts vectors and metadata payloads into the embedded Qdrant collection on local disk.

### 4.2 Querying Workflow
1. User submits a search query via Web UI or CLI:
   - Case A: Text query (`"leather swivel chair"`)
   - Case B: Image query (`"test_chair.png"`)
2. `SigLIP2Service` encodes the query into a 768d unit vector.
3. `VectorStore` executes an HNSW nearest-neighbor search against the local collection using Cosine distance.
4. `SearchEngine` evaluates similarity scores:
   - $\text{Score} \ge 0.85$: Flagged as **Exact Match**.
   - $0.65 \le \text{Score} < 0.85$: Flagged as **High Similarity**.
   - $0.50 \le \text{Score} < 0.65$: Flagged as **Moderate Semantic Match**.
5. Results are returned with thumbnail preview, category, score, and absolute USD filepath.

---

## 5. Technology Choices & Rationale

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Core Language** | Python 3.10+ | Native support for PyTorch, Hugging Face, Qdrant client, and USD tooling. |
| **Embedding Model** | `google/siglip2-base-patch16-224` | 86M params, pairwise sigmoid loss for calibrated similarities, 109-language support, runs in ~1GB VRAM. |
| **Vector Database** | Embedded `qdrant-client` (`path="./data/qdrant_db"`) | Zero Docker/daemon dependency; in-process on-disk persistence; native JSON payload filtering. |
| **Deep Learning Framework** | `torch` + `transformers` | Industry standard; direct CUDA GPU hardware acceleration on Windows. |
| **Web Interface** | `streamlit` | Zero frontend boilerplate; renders image thumbnails, sliders, and file pickers seamlessly on `localhost`. |

---

## 6. Key Design Decisions
- **Embedded over Client-Server**: Eliminates background daemon management and port conflicts on developer workstations (ADR-002).
- **Pre-rendered Thumbnail Fast Path**: Takes advantage of Omniverse/USD kit existing assets to make initial indexing take seconds instead of hours (ADR-003).
- **Two-Phase Viewpoint Evolution (ADR-004)**: Phase 1 indexes single front auto-thumbnails to deliver the core MVP immediately. Phase 2 introduces 2x2 turntable contact sheets ($0^\circ, 90^\circ, 180^\circ, 270^\circ$) to resolve perspective bias and occlusion gaps without complicating the 1-to-1 Qdrant vector schema.
- **Cosine Metric Normalization**: Vectors are normalized at inference time so cosine similarity maps linearly to $[0, 1]$ for reliable thresholding.

---

## 7. Open Questions
*All key architectural questions have been resolved via ADR-001, ADR-002, and ADR-003. No remaining blocking architectural questions.*

