---
type: Architecture Decision Record
title: "Architecture Decisions: ID-104 Local USD Multimodal Search Engine"
description: "Architectural decision records tracking design alternatives, trade-offs, and decisions for the 100% local SigLIP 2 USD retrieval engine."
tags: [sdlc, adr, architecture, local-first, qdrant, siglip2]
status: approved
generated:
  by: spec-first-sdlc
  at: "2026-11-08T19:48:00-03:00"
---

# Architecture Decisions: ID-104 Local USD Multimodal Search Engine

**Last Updated:** 2026-11-08  
**Project ID:** ID-104  

---

## ADR-001: Local Embedding Backbone Selection (SigLIP 2 vs CLIP vs OpenShape)

**Status:** Accepted  

**Context:**  
The engine requires zero-shot text-to-image and image-to-image retrieval capabilities running 100% locally on a Windows workstation. Models must align textual descriptions with visual thumbnails of 3D assets.

**Decision:**  
Adopt Google DeepMind's **SigLIP 2** (`google/siglip2-base-patch16-224` as default, configurable to `siglip2-so400m-patch14-384`) using local PyTorch and Hugging Face Transformers.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **SigLIP 2 (Selected)** | State-of-the-art zero-shot retrieval; pairwise sigmoid loss gives superior calibrated similarity scores; native multilingual support; lightweight base model (~86M params, ~1GB VRAM). | Requires 2D visual projections of 3D assets rather than raw point clouds. |
| **OpenAI CLIP ViT-B/32** | Established ecosystem; widespread examples. | Inferior retrieval performance compared to SigLIP 2; softmax loss suffers from batch scaling effects; weaker localization and detail representation. |
| **OpenShape / ULIP-2 (3D Point Encoders)** | Operates directly on 3D point cloud geometry. | Requires heavy 3D point sampling preprocessing; slower local inference; less flexible text-query vocabulary; difficult Windows C++ dependency management. |

**Rationale:**  
SigLIP 2 delivers top-tier vision-language retrieval accuracy with minimal local compute overhead. Combined with pre-rendered thumbnails found in Omniverse/USD libraries, it circumvents heavy 3D mesh rendering bottlenecks.

**Consequences:**  
- Fast local inference (<20ms per query on GPU).
- Depend on 2D preview images (pre-rendered `.thumbs/` or headless fallback).

---

## ADR-002: Local Vector Database Selection (Embedded Qdrant vs FAISS vs Chroma)

**Status:** Accepted  

**Context:**  
The application must store and query dense vectors (768-dim) alongside metadata (file paths, categories, timestamps) strictly on local disk without requiring an external database server or Docker daemon.

**Decision:**  
Use **Qdrant in embedded mode** via `qdrant-client` targeting a local disk directory (`50_PROJECT/data/qdrant_db/`).

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Qdrant Embedded (Selected)** | In-process execution via local disk storage; zero Docker/daemon needed; built-in HNSW index; native rich payload filtering (category, path, size); production-grade query syntax. | Slightly larger Python binary footprint than pure NumPy. |
| **FAISS (Flat / HNSW)** | Fastest raw matrix operations in RAM. | Not a database; requires custom SQLite or JSON sidecar mapping to store asset metadata and file paths; manual index serialization. |
| **ChromaDB** | Simple `pip install`; local persistence. | Higher query latency and memory overhead; SQLite locks on concurrent operations; less flexible filtering. |

**Rationale:**  
Embedded Qdrant combines the best of both worlds: zero installation friction (no Docker/cloud) and a full-featured vector database engine with native metadata filtering.

**Consequences:**  
- Persistent storage stored cleanly under `50_PROJECT/data/qdrant_db/`.
- Instantaneous filtering by category (e.g., `Commercial`, `Industrial`, `Residential`) during similarity search.

---

## ADR-003: 3D Asset Visual Ingestion Strategy (Thumbnail Parsing vs On-The-Fly Hydra Rendering)

**Status:** Accepted  

**Context:**  
USD files cannot be directly fed to 2D vision models. The engine needs visual representations for each asset in `D:\___tmp\USD_assets`.

**Decision:**  
Adopt a **hybrid priority ingestion strategy**:
1. **Primary Path (Fast Ingestion)**: Automatically detect and ingest existing pre-rendered thumbnails located at `<Folder>/.thumbs/256x256/<asset>.usd.auto.png` (created by Omniverse / USD asset kits).
2. **Fallback Path (On-Demand)**: For assets without pre-rendered thumbnails, provide a fallback utility utilizing `usdrecord` / `pxr.UsdImagingGL` or placeholder logging.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Pre-Rendered Thumbs + Fallback (Selected)** | Instantaneous index generation for existing collections; zero GPU OpenGL headless setup required for 95%+ of assets; sub-second scanning. | Relies on pre-baked thumbnails for the fast path. |
| **Render Every Asset via Hydra/Storm** | Guaranteed fresh renders from multiple custom angles. | Very slow ingestion (seconds per asset); complex OpenGL/Hydra context setup on headless Windows scripts. |

**Rationale:**  
Physical inspection of `D:\___tmp\USD_assets` confirmed that all collections (`Commercial`, `Industrial`, `Residential`) already contain `.thumbs/256x256/` previews. Leveraging them achieves near-instantaneous database construction.

**Consequences:**  
- Ingestion speed of hundreds of assets in under 30 seconds.
- Modular renderer fallback remains available when new un-thumbnailed assets are added.


---

## ADR-004: Perspective Bias Mitigation & Multi-View Evolutionary Roadmap

**Status:** Accepted (derived from `wiki/_artifacts/ID-104_GapAnalysisReport.md`)

**Context:**  
Using only a single front/isometric thumbnail (`.thumbs/256x256/*.usd.auto.png`) creates viewpoint blind spots, occlusion bias (e.g., hidden rear controls, adjustment levers), planar depth ambiguity, and query-angle fragility when searching by reference image.

**Decision:**  
Formally divide the visual representation architecture into a **two-phase phased evolution**:
1. **Phase 1 (Active MVP)**: Use the single auto-thumbnail fast-path. Calibrate similarity thresholds to account for single-perspective uncertainty ($\ge 0.82$ Exact Match, $0.65-0.81$ High Similarity, $0.50-0.64$ Semantic Match with a perspective note).
2. **Phase 2 (Target Evolution)**: Adopt a **2x2 Contact Sheet Mosaic** representation. Render 4 turntable viewpoints ($0^\circ, 90^\circ, 180^\circ, 270^\circ$) and stitch them into a single $512\times512$ 4-grid composite image before computing the SigLIP 2 embedding.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **2x2 Contact Sheet Mosaic (Selected for Phase 2)** | Grants $360^\circ$ visibility in a single forward pass; maintains clean 1-to-1 vector mapping in Qdrant; zero multi-vector query complexity. | Requires offline 4-view render pass. |
| **Multi-Vector per Asset (MaxSim / ColBERT)** | Native matching against arbitrary camera angles. | Multiplies Qdrant index size by $4\times$; complicates payload schemas and scoring logic. |
| **Remain Exclusively Single-View** | Zero rendering setup. | Permanently leaves rear/interior attributes unsearchable; fragile image-to-image queries. |

**Rationale:**  
The 2x2 mosaic strategy achieves full $360^\circ$ semantic coverage while preserving the architectural simplicity of 1-to-1 vector points in embedded Qdrant, solving the gap identified in `ID-104_GapAnalysisReport.md`.

**Consequences:**  
- Phase 1 delivers immediate, sub-second local retrieval without OpenGL dependencies.
- Phase 2 implementation spec is defined with a non-breaking database schema upgrade.
