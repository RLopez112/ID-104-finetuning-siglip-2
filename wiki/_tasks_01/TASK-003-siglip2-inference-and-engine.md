---
type: Task Runbook
id: TASK-003
title: SigLIP 2 Inference Service & Search Engine Orchestration
description: "Implement local SigLIP 2 feature extraction for text and images, and orchestrate search matching with calibrated confidence thresholds."
resource: repo://50_PROJECT/src/model_service.py
status: completed
assigned_profiles:
  - AI Developer
  - Backend Developer
change_ticket: null
dependencies:
  - TASK-000
  - TASK-001
  - TASK-002
eis_reference: "wiki/_specs/ID-104_EIS.md#32-siglip2service-srcmodel_servicepy"
affected_files:
  - "[CREATE] 50_PROJECT/src/model_service.py"
  - "[CREATE] 50_PROJECT/src/engine.py"
  - "[CREATE] 50_PROJECT/tests/test_engine.py"
tags: [siglip2, inference, multimodal, text-to-image, image-to-image]
generated:
  by: task-implementation-planner
  at: "2026-11-08T20:09:00-03:00"
---

# TASK-003: SigLIP 2 Inference Service & Search Engine Orchestration

## GENERAL DESCRIPTION
Implement the local deep learning inference module `50_PROJECT/src/model_service.py` loading Google SigLIP 2 (`google/siglip2-base-patch16-224`) on local GPU/CPU hardware to generate L2-normalized 768-dim embeddings for text and images, and integrate with `50_PROJECT/src/engine.py` to classify search results into Exact Match, High Similarity, and Semantic Match per [[ID-104_EIS.md#32-siglip2service-srcmodel_servicepy](wiki/_specs/ID-104_EIS.md#32-siglip2service-srcmodel_servicepy)] and [[ID-104_EIS.md#34-searchengine-srcenginepy](wiki/_specs/ID-104_EIS.md#34-searchengine-srcenginepy)].

## EXPECTED RESULT
`SigLIP2Service.encode_text()` and `encode_image()` produce 768-dimensional float32 unit vectors. `SearchEngine.search_text()` and `search_image()` return typed `SearchResponse` objects with accurate match classification per [[ID-104_EIS.md#22-search-query--result-model-enginepy](wiki/_specs/ID-104_EIS.md#22-search-query--result-model-enginepy)].

## CODE REFERENCE
- `[CREATE] 50_PROJECT/src/model_service.py`: Implement `SigLIP2Service` with FP16 CUDA acceleration and automatic CPU fallback per [[ID-104_EIS.md#32-siglip2service-srcmodel_servicepy](wiki/_specs/ID-104_EIS.md#32-siglip2service-srcmodel_servicepy)].
- `[CREATE] 50_PROJECT/src/engine.py`: Implement `SearchEngine` with `search_text`, `search_image`, and threshold badge evaluation per [[ID-104_EIS.md#34-searchengine-srcenginepy](wiki/_specs/ID-104_EIS.md#34-searchengine-srcenginepy)].
- `[CREATE] 50_PROJECT/tests/test_engine.py`: Unit and integration tests testing text encoding, dummy image encoding, vector normalization, and mock query scoring.

## VALIDATION CRITERIA
- Unit tests pass with `torch.norm(vector) == pytest.approx(1.0, 1e-4)`.
- Query latency is <100ms on GPU for single text prompts.
- Exact match threshold ($\ge 0.82$) correctly flags identical reference image queries.

## RISKS
- First run weights download failure; handled via Hugging Face automatic local cache in `~/.cache/huggingface/hub/`.

## SUBSTEPS
1. Implement `SigLIP2Service` with dynamic device selection (CUDA/CPU) and L2 normalization per [[ID-104_EIS.md#32-siglip2service-srcmodel_servicepy](wiki/_specs/ID-104_EIS.md#32-siglip2service-srcmodel_servicepy)].
2. Implement `SearchEngine` executing end-to-end multimodal search workflows per [[ID-104_EIS.md#34-searchengine-srcenginepy](wiki/_specs/ID-104_EIS.md#34-searchengine-srcenginepy)].
3. Apply confidence threshold badges per ADR-004 ($0.82$ exact, $0.65$ similar).
4. Author test suite in `50_PROJECT/tests/test_engine.py` and verify.

