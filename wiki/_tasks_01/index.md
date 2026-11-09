# ID-104 Master Task Index: Batch 01

Master progressive disclosure task index for **ID-104: 100% Local USD Multimodal Search & Retrieval Engine**.

- **Batch Directory**: `wiki/_tasks_01/`
- **Governing EIS**: [`wiki/_specs/ID-104_EIS.md`](../_specs/ID-104_EIS.md)
- **Governing ADRs**: [`wiki/_specs/ID-104_ADR.md`](../_specs/ID-104_ADR.md) (ADR-001 to ADR-004)
- **Status**: Ready / In Progress

---

## Batch Tasks

| Task ID | Title | Assigned Profiles | Change Ticket | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [TASK-000](TASK-000-environment-and-dependencies.md) | Environment, Tooling & GPU Bootstrap | AI Developer, Backend Developer | N/A | None | Completed |
| [TASK-001](TASK-001-usd-asset-and-thumbnail-scanner.md) | USD Asset & Auto-Thumbnail Scanner | Backend Developer, Omniverse Developer | N/A | TASK-000 | Completed |
| [TASK-002](TASK-002-embedded-qdrant-vector-store.md) | Embedded Qdrant Vector Store Manager | Backend Developer, Data Scientist | N/A | TASK-000, TASK-001 | Completed |
| [TASK-003](TASK-003-siglip2-inference-and-engine.md) | SigLIP 2 Inference & Search Orchestration | AI Developer, Backend Developer | N/A | TASK-000, TASK-001, TASK-002 | Completed |
| [TASK-004](TASK-004-cli-and-streamlit-dashboard.md) | CLI Runner & Streamlit Localhost Dashboard | Frontend Developer, Backend Developer | N/A | TASK-000 to TASK-003 | Completed |
| [TASK-005](TASK-005-integration-and-benchmark-validation.md) | End-to-End Integration & Benchmark Suite | Testing Engineer, AI Developer | N/A | TASK-000 to TASK-004 | Completed |

---

## Bug Fixes & Patch Tasks

*No active bug fix tasks reported for Batch 01. Any future bug patch runbooks will be routed into `wiki/_tasks_01/bugs/`.*

---

## Execution & Milestone Gates
1. **Milestone 1 (Foundational Setup)**: Complete TASK-000 and TASK-001 $\rightarrow$ Python 3.12 GPU environment verified and USD assets scanned with thumbnails.
2. **Milestone 2 (Core Engine)**: Complete TASK-002 and TASK-003 $\rightarrow$ Embedded Qdrant vector database initialized and SigLIP 2 feature extraction operational.
3. **Milestone 3 (Interfaces & Delivery)**: Complete TASK-004 and TASK-005 $\rightarrow$ CLI and Streamlit UI operational with all unit and integration tests passing.

