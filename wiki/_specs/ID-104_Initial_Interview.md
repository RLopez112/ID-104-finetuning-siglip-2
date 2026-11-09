---
type: Software Requirements Interview Record
title: "Technical Requirements Interview: ID-104 Local USD Multimodal Search Engine"
description: "Consolidated record of technical stakeholder requirements, architectural trade-offs, operational scope, and verification criteria for the strictly local SigLIP 2 USD retrieval engine."
tags: [sdlc, requirements, interview, srs, local-first, siglip2, qdrant]
status: approved
generated:
  by: software-interviewer
  at: "2026-11-08T19:57:00-03:00"
---

# Technical Requirements Interview: ID-104 Local USD Multimodal Search Engine

**Project ID:** ID-104  
**Date:** 2026-11-08  
**Scope:** Strictly Local / Offline-Capable Multimodal Retrieval Engine  
**Author / Interviewer:** Software Interviewer Skill  

---

## 1. Executive Summary & Problem Definition
- **Problem Statement (Q1)**: Local 3D OpenUSD asset libraries (`D:\___tmp\USD_assets`) lack descriptive metadata or taxonomy tags. Filenames (e.g., `Boat.usd`, `Roland.usd`) prevent intuitive semantic discovery.
- **Target Audience & Users (Q2)**: Local 3D artists, game developers, VFX supervisors, and Digital Twin engineers working in standalone workstation environments.
- **Success Criteria (Q3)**: 
  - Sub-second query response time (<500ms) with high top-5 relevance accuracy for exact and visually similar USD models.
  - Sub-2-minute complete catalog ingestion of target USD assets without memory crashes or memory leaks.
  - Zero-configuration ease of use (single command/script to launch and search).

---

## 2. Constraints, Governance & Operations
- **Hosting & Deployment Target (Q15)**: 100% Local workstation environment (`localhost`), zero cloud services, zero external network API calls. Air-gap capable once weights are locally cached.
- **Scale & Concurrency (Q16)**: Single desktop workstation user (local interactive session with sequential or low-concurrency queries).
- **Data Location (Q10)**: 
  - Assets: `D:\___tmp\USD_assets` (local drive).
  - Embeddings & Metadata: Local disk storage under `50_PROJECT/data/qdrant_db/`.
- **IP & Security Rules (Q11)**: Strict confidentiality; no asset geometry, previews, or queries may be transmitted across the public internet.
- **Out of Scope (Q13)**: Cloud SaaS hosting, distributed multi-user clustering, real-time in-app USD geometry editing/authoring, generative 3D mesh synthesis.

---

## 3. Architecture & Technology Decisions
- **Embedding Backbone (Q19)**: Google **SigLIP 2** (`google/siglip2-base-patch16-224` default, 86M params, ~1GB VRAM, pairwise sigmoid loss for calibrated cosine scores) via PyTorch and Hugging Face Transformers.
- **Vector Storage (Q10, Q19)**: **Embedded Qdrant** (`qdrant-client` targeting local directory `50_PROJECT/data/qdrant_db/`), running in-process without Docker containers or daemon setup.
- **User Interface & Integration (Q8, Q9, Q20)**: Standalone local Python UI (Streamlit) running on `localhost` alongside a scriptable CLI command runner (`cli.py`).
- **Asset Ingestion Strategy**: Fast-path indexing scanning `D:\___tmp\USD_assets` and pairing each `.usd` file with its pre-rendered `.thumbs/256x256/*.usd.auto.png` preview.

---

## 4. MVP Boundary & Verification Plan
- **MVP Definition (Q20, Q21)**:
  - Directory scanner resolving USD files and associated thumbnails across Commercial, Industrial, and Residential directories in `D:\___tmp\USD_assets`.
  - Batch SigLIP 2 feature extractor creating normalized 768d visual vectors.
  - Embedded Qdrant collection upserting vectors with file metadata (`usd_path`, `thumb_path`, `category`, `filesize`).
  - Text-to-USD search (natural language prompt -> 768d vector -> cosine search -> ranked USD results).
  - Image-to-USD search (reference image upload -> 768d vector -> cosine search -> exact/similar matches).
  - Streamlit localhost dashboard with visual preview cards, similarity scores, and copyable file paths.
  - Scriptable CLI runner for terminal query execution.
- **Testing & Verification (Q17)**:
  - Automated unit and integration tests (Pytest) validating vector dimensionality, indexing routines, exact-match retrieval, and mock query latency.

