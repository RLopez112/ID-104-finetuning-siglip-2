---
project_id: ID-104
project_name: SigLIP 2 Vision-Language Fine-Tuning Lab - USD Multimodal Search Engine
last_updated: 2026-11-08T21:12:00-03:00
current_sdlc_phase: EIS Implemented / Sprint 1 Complete / Pre-ADR-005
active_task_folder: wiki/_tasks_01/
active_sprint: Sprint 1 (Core USD Multimodal Search Engine)
type: active_context
---

# Active Context Snapshot: ID-104

## 1. Project High-Level State
- **Workspace**: `F:\PERSONALES\_PROJECTS\ID-104-finetuning-siglip-2`
- **Objective**: Build a 100% local, offline-capable multimodal search engine for OpenUSD 3D asset libraries (661 assets at `D:\___tmp\USD_assets`) using Google SigLIP 2 (`google/siglip2-base-patch16-224`, 768-dim) and an embedded on-disk Qdrant vector database (`50_PROJECT/data/qdrant_db/`).
- **Phase**: **Sprint 1 Complete**. Core engine, CLI, Streamlit web UI, and automated test suite (8/8 tests passing) are fully operational. Comprehensive architecture and implementation reports documented.

## 2. In-Progress & Completed Tasks
- [x] **TASK-000**: Workspace initialization, Python 3.12 virtual environment, and dependency validation (`torch 2.6.0+cu124`, `qdrant-client`, `transformers`, `usd-core`).
- [x] **TASK-001**: USD asset crawler and thumbnail resolver (`50_PROJECT/src/scanner.py`) discovering 661 models with deterministic UUIDv5 IDs.
- [x] **TASK-002**: Embedded local Qdrant collection manager (`50_PROJECT/src/vector_store.py`).
- [x] **TASK-003**: SigLIP 2 local vision-language inference service with FP16 CUDA acceleration (`50_PROJECT/src/model_service.py`).
- [x] **TASK-004**: Multimodal search orchestrator and calibrated confidence badging (`50_PROJECT/src/engine.py`).
- [x] **TASK-005**: CLI runner (`cli.py`), Streamlit localhost web app (`app.py`), and test suite (`tests/`, 8/8 passing).
- [ ] **NEXT (ADR-005)**: OpenUSD scene graph metadata extraction (materials, prims, bounding box dimensions) and hybrid vector fusion ($0.65 \times \mathbf{v}_{\text{visual}} + 0.35 \times \mathbf{v}_{\text{text}}$).
- [ ] **Sprint 2 Roadmap (ADR-004)**: Headless offscreen 2x2 turntable contact sheet mosaic generator (`pxr.UsdImagingGL`).

## 3. Key Architectural Decisions (ADRs)
- **ADR-001**: Google SigLIP 2 Base Patch16 224 as multimodal encoder (768-dim, native Gemma tokenizer).
- **ADR-002**: Embedded local Qdrant on workstation NVMe (`50_PROJECT/data/qdrant_db/`) with Cosine distance metric.
- **ADR-003**: Phase 1 Fast-Path pre-rendered Omniverse auto-thumbnails (`.thumbs/256x256/*.usd.auto.png`).
- **ADR-004**: Calibrated confidence thresholds for asymmetric cosine distributions (Image: 0.82/0.65; Text: 0.125/0.095/0.070).
- **ADR-005 (Proposed)**: Native OpenUSD metadata traversal via `usd-core` / `pxr.Usd` and linear hybrid vector fusion.

## 4. Operational & Environment Status
- **OS / Hardware**: Windows 11, NVIDIA GeForce RTX 4070 Ti (12GB VRAM), CUDA 12.4.
- **Python**: 3.12.10 (`.venv`).
- **Local Database**: 661 models indexed into embedded Qdrant in 20.76s.
- **Streamlit Web UI**: Running at `http://localhost:8501`.
- **Query Latency**: Text query $\approx 350\text{ms}$; Image query $\approx 420\text{ms}$.

## 5. Immediate Blockers & Risks
- **Blockers**: None. Core system fully operational and verified.
- **Risks / Watch-outs**: When implementing `pxr.Usd` in `scanner.py`, ensure `PXR_USDC_EMIT_DEPRECATION_WARNINGS=0` is set to suppress 0.7.0 crate version notices from Omniverse USD files.

