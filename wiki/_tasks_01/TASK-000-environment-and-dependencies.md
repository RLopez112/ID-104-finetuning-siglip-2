---
type: Task Runbook
id: TASK-000
title: Environment, Tooling, and GPU Dependency Bootstrap
description: "Initialize isolated Python 3.12 virtual environment, install PyTorch with CUDA 12.4 acceleration, transformers, qdrant-client, pillow, and smoke test script."
resource: repo://50_PROJECT/requirements.txt
status: completed
assigned_profiles:
  - AI Developer
  - Backend Developer
change_ticket: null
dependencies: []
eis_reference: "wiki/_specs/ID-104_EIS.md#1-directory-structure--layout"
affected_files:
  - "[CREATE] 50_PROJECT/requirements.txt"
  - "[CREATE] 50_PROJECT/src/config.py"
  - "[CREATE] 50_PROJECT/scripts/check_env.py"
tags: [bootstrap, venv, cuda, pytorch, qdrant, siglip2]
generated:
  by: task-implementation-planner
  at: "2026-11-08T20:09:00-03:00"
---

# TASK-000: Environment, Tooling, and GPU Dependency Bootstrap

## GENERAL DESCRIPTION
Configure the local workstation environment for 100% offline execution, establishing an isolated Python 3.12 virtual environment (`.venv`), installing GPU-accelerated PyTorch with CUDA 12.4 runtime, Hugging Face `transformers`, embedded `qdrant-client`, `pillow`, and validating environment readiness per [[ID-104_EIS.md#1-directory-structure--layout](wiki/_specs/ID-104_EIS.md#1-directory-structure--layout)].

## EXPECTED RESULT
An activated Python virtual environment capable of executing CUDA GPU tensor operations on the local RTX 4070 Ti, with all dependencies verified via an automated smoke test script exiting with code 0 per [[ID-104_EIS.md#1-directory-structure--layout](wiki/_specs/ID-104_EIS.md#1-directory-structure--layout)].

## CODE REFERENCE
- `[CREATE] 50_PROJECT/requirements.txt`: Pinned manifests for `torch`, `transformers`, `qdrant-client`, `streamlit`, and `pytest`.
- `[CREATE] 50_PROJECT/src/config.py`: Centralized configuration constants (paths, thresholds, collection names) per [[ID-104_EIS.md#1-directory-structure--layout](wiki/_specs/ID-104_EIS.md#1-directory-structure--layout)].
- `[CREATE] 50_PROJECT/scripts/check_env.py`: Smoke test asserting PyTorch CUDA availability, Qdrant client instantiation, and directory existence.

## VALIDATION CRITERIA
- `python 50_PROJECT/scripts/check_env.py` exits with code 0 and reports `CUDA available: True`.
- `qdrant_client` imports and executes in embedded mode without external port/daemon bindings.

## RISKS
- CUDA version mismatch; mitigated by targeting pre-built `cu124` PyTorch wheels compatible with local NVIDIA driver 617.42.

## SUBSTEPS
1. Create and activate Python 3.12 virtual environment (`.venv`) per [[ID-104_EIS.md#1-directory-structure--layout](wiki/_specs/ID-104_EIS.md#1-directory-structure--layout)].
2. Install pinned dependencies from `50_PROJECT/requirements.txt`.
3. Implement `50_PROJECT/src/config.py` with default paths and model configurations per [[ID-104_EIS.md#1-directory-structure--layout](wiki/_specs/ID-104_EIS.md#1-directory-structure--layout)].
4. Create and execute `50_PROJECT/scripts/check_env.py` smoke test script.

