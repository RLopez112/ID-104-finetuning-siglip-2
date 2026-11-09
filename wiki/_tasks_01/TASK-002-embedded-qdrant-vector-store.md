---
type: Task Runbook
id: TASK-002
title: Embedded Qdrant Vector Store Manager
description: "Implement in-process local Qdrant collection management, point upserting with JSON payloads, and cosine similarity querying."
resource: repo://50_PROJECT/src/vector_store.py
status: completed
assigned_profiles:
  - Backend Developer
  - Data Scientist
change_ticket: null
dependencies:
  - TASK-000
  - TASK-001
eis_reference: "wiki/_specs/ID-104_EIS.md#33-localvectorstore-srcvector_storepy"
affected_files:
  - "[CREATE] 50_PROJECT/src/vector_store.py"
  - "[CREATE] 50_PROJECT/tests/test_vector_store.py"
tags: [qdrant, vector-db, hnsw, embedded, storage]
generated:
  by: task-implementation-planner
  at: "2026-11-08T20:09:00-03:00"
---

# TASK-002: Embedded Qdrant Vector Store Manager

## GENERAL DESCRIPTION
Implement the local vector database wrapper in `50_PROJECT/src/vector_store.py` using `qdrant-client` in embedded storage mode targeting `50_PROJECT/data/qdrant_db/`, managing collection creation (768-dim, Cosine distance), point upserts with full metadata payloads, and filtered similarity retrieval per [[ID-104_EIS.md#33-localvectorstore-srcvector_storepy](wiki/_specs/ID-104_EIS.md#33-localvectorstore-srcvector_storepy)].

## EXPECTED RESULT
Embedded Qdrant client initializes on local disk, stores normalized 768d vectors, and returns ranked nearest neighbors filtered by category with sub-millisecond query latency per [[ID-104_EIS.md#33-localvectorstore-srcvector_storepy](wiki/_specs/ID-104_EIS.md#33-localvectorstore-srcvector_storepy)].

## CODE REFERENCE
- `[CREATE] 50_PROJECT/src/vector_store.py`: Implement `LocalVectorStore` class with `upsert_records`, `search`, `count`, and `clear` per [[ID-104_EIS.md#33-localvectorstore-srcvector_storepy](wiki/_specs/ID-104_EIS.md#33-localvectorstore-srcvector_storepy)].
- `[CREATE] 50_PROJECT/tests/test_vector_store.py`: Unit tests validating collection creation, mock vector upserting, category filtering, and count queries on temporary test stores.

## VALIDATION CRITERIA
- `pytest 50_PROJECT/tests/test_vector_store.py` passes with 100% green assertions.
- Vector persistence is maintained across client reinvocations on disk without data corruption.

## RISKS
- SQLite lock contention if multiple processes open the same embedded directory concurrently; mitigated by single-workstation sequential access model documented in ADR-002.

## SUBSTEPS
1. Implement `LocalVectorStore.__init__` with automatic directory provisioning and collection creation per [[ID-104_EIS.md#33-localvectorstore-srcvector_storepy](wiki/_specs/ID-104_EIS.md#33-localvectorstore-srcvector_storepy)].
2. Implement `upsert_records` transforming `USDAssetRecord` instances and numpy matrices into Qdrant `PointStruct` objects.
3. Implement `search` with optional `FieldCondition` payload filtering for `category`.
4. Author unit tests in `50_PROJECT/tests/test_vector_store.py` and verify execution.

