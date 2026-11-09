---
type: Task Runbook
id: TASK-005
title: End-to-End Integration, Regression, and Benchmark Validation
description: "Run comprehensive integration test suite, verify catalog indexing on target directory D:\___tmp\USD_assets, validate retrieval latency, and test edge cases."
resource: repo://50_PROJECT/tests/
status: completed
assigned_profiles:
  - Testing Engineer
  - AI Developer
change_ticket: null
dependencies:
  - TASK-000
  - TASK-001
  - TASK-002
  - TASK-003
  - TASK-004
eis_reference: "wiki/_specs/ID-104_EIS.md#5-traceability-matrix"
affected_files:
  - "[CREATE] 50_PROJECT/tests/test_integration_e2e.py"
  - "[MODIFY] wiki/log.md"
tags: [integration, regression, e2e, testing, benchmark]
generated:
  by: task-implementation-planner
  at: "2026-11-08T20:09:00-03:00"
---

# TASK-005: End-to-End Integration, Regression, and Benchmark Validation

## GENERAL DESCRIPTION
Execute comprehensive automated integration and regression testing across the entire system. Verify real catalog scanning on `D:\___tmp\USD_assets`, validate vector normalization, execute text-to-USD and image-to-USD queries, benchmark query response times (<500ms target), and document verification results per [[ID-104_EIS.md#5-traceability-matrix](wiki/_specs/ID-104_EIS.md#5-traceability-matrix)].

## EXPECTED RESULT
Complete test suite passes with 100% green status across `test_scanner.py`, `test_vector_store.py`, `test_engine.py`, and `test_integration_e2e.py`. Target catalog in `D:\___tmp\USD_assets` is indexed and queryable via CLI and Streamlit per [[ID-104_EIS.md#5-traceability-matrix](wiki/_specs/ID-104_EIS.md#5-traceability-matrix)].

## CODE REFERENCE
- `[CREATE] 50_PROJECT/tests/test_integration_e2e.py`: End-to-end integration test executing real scan, temporary vector store creation, and simulated text/image queries.
- `[MODIFY] wiki/log.md`: Append verification milestones and test execution logs.

## VALIDATION CRITERIA
- `pytest 50_PROJECT/tests/` passes without errors or failures.
- Benchmark assertion: Average query execution latency $\le 500\text{ ms}$ on workstation hardware.
- Exact match image retrieval returns top-1 score $\ge 0.82$.

## RISKS
- Potential cold-start latency on the first query after model loading; mitigated by running a warm-up dummy pass during service initialization.

## SUBSTEPS
1. Create `50_PROJECT/tests/test_integration_e2e.py` covering full lifecycle from scanning to querying per [[ID-104_EIS.md#5-traceability-matrix](wiki/_specs/ID-104_EIS.md#5-traceability-matrix)].
2. Run full test suite: `pytest 50_PROJECT/tests/ -v`.
3. Perform benchmark verification of text-to-USD search latency.
4. Verify CLI indexing against `D:\___tmp\USD_assets`.
5. Update `wiki/log.md` with final verification status.

