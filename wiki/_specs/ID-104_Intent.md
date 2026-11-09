---
type: Project Intent
title: "Project Intent: ID-104 SigLIP 2 Local USD Multimodal Search Engine"
description: "Intent, constraints, and scope definition for a strictly local, offline-capable multimodal search and retrieval engine for OpenUSD 3D assets using SigLIP 2 embeddings."
tags: [sdlc, intent, requirements, local-first, siglip2, openusd]
status: approved
generated:
  by: spec-first-sdlc
  at: "2026-11-08T19:48:00-03:00"
---

# Project Intent: ID-104 - 100% Local USD Multimodal Search & Retrieval Engine

**Project ID:** ID-104  
**Date:** 2026-11-08  
**Status:** Approved  
**Upstream Artifacts:** `wiki/_artifacts/ID-104_FirstApproach.md`, `wiki/_artifacts/ID-104_DeepResearch.md`

---

## 1. Problem Statement
3D asset libraries (such as USD/USDA/USDC models in `D:\___tmp\USD_assets`) lack standardized semantic metadata. Studio artists and engineers cannot easily search 3D assets by natural language or visual references because filenames (e.g., `Boat.usd`, `Roland.usd`) do not capture visual appearance or functional attributes. Furthermore, proprietary 3D geometry cannot be uploaded to remote cloud APIs due to IP confidentiality, latency, and air-gapped environment constraints.

## 2. Core Intent & Objectives
Develop a **100% local, offline-capable, standalone multimodal search and retrieval tool** that:
1. Ingests local OpenUSD assets from `D:\___tmp\USD_assets` (utilizing pre-rendered `.thumbs/256x256/*.usd.auto.png` thumbnails, with fallback rendering capability).
2. Generates vision-language embeddings using **Google SigLIP 2** (`google/siglip2-base-patch16-224` or `siglip2-so400m-patch14-384`) running locally on CUDA GPU (or CPU).
3. Stores vector embeddings and file metadata into a **local embedded vector database** (embedded Qdrant on-disk).
4. Provides multimodal search interfaces (CLI and local Web UI) supporting:
   - **Text-to-USD**: Search using natural descriptive queries (e.g., "leather executive swivel chair", "industrial generator").
   - **Image-to-USD**: Search using a local reference image to find exact matches or visually similar 3D assets.
   - **Filtering & Scoring**: Calibrated cosine similarity scoring with thresholding to distinguish exact matches from near neighbors, plus category filtering (`Commercial`, `Industrial`, `Residential`).

## 3. Key Constraints
- **Strictly Local & Offline-Capable**: Zero cloud APIs, zero external SaaS vector databases, zero telemetry. Once model weights are locally cached, all operations must function without network connectivity.
- **Embedded Storage**: Vector database must run in-process or serverless via disk storage (`50_PROJECT/data/qdrant_db/`), avoiding mandatory external Docker containers or socket configurations.
- **Hardware Footprint**: Compatible with modern Windows workstations with NVIDIA GPUs (sub-2GB VRAM allocation for base model) and graceful CPU execution fallback.
- **Modularity & Traceability**: Clean separation between asset scanner, embedding generator, vector storage client, and user interface.

