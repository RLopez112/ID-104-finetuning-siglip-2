---
type: Implementation Spec
title: "Implementation Specification: ID-104 Local USD Multimodal Search Engine"
description: "Detailed executable implementation contract including module interfaces, data models, state machines, persistence schemas, CLI commands, and test specifications for the 100% local SigLIP 2 USD retrieval engine."
resource: repo://50_PROJECT/src/
tags: [sdlc, eis, api, database, tests, local-first, siglip2, qdrant]
status: active
generated:
  by: spec-first-sdlc
  at: "2026-11-08T19:58:00-03:00"
---

# Implementation Specification: ID-104 Local USD Multimodal Search Engine

**Version:** 1.0  
**Date:** 2026-11-08  
**Based on:** HLD v1.0, ADR-001/002/003/004, and `wiki/_specs/ID-104_Initial_Interview.md`

---

## 1. Directory Structure & Layout
Source code and persistent data reside under `50_PROJECT/`:

```
50_PROJECT/
├── data/
│   └── qdrant_db/               # Local on-disk Qdrant embedded storage
├── src/
│   ├── __init__.py
│   ├── config.py                # Paths, model names, confidence thresholds
│   ├── scanner.py               # USD & .thumbs/ asset discovery
│   ├── model_service.py         # SigLIP 2 PyTorch model loader & encoder
│   ├── vector_store.py          # Embedded Qdrant collection manager
│   ├── engine.py                # High-level search orchestration
│   ├── cli.py                   # Scriptable CLI runner (index / search)
│   └── app.py                   # Localhost Streamlit dashboard
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py          # Tests for thumbnail & metadata resolution
│   ├── test_vector_store.py     # Tests for local Qdrant collection & search
│   └── test_engine.py           # Integration tests for text/image search flows
└── requirements.txt             # Pinned local dependencies
```

---

## 2. Data Models & Schemas

### 2.1 Asset Metadata Record (`scanner.py`)
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class USDAssetRecord:
    asset_id: str             # Unique SHA-256 or sanitized relative path hash
    usd_path: str             # Absolute path to .usd / .usda / .usdc
    thumbnail_path: str       # Absolute path to preview image (.png / .jpg)
    category: str             # e.g., 'Commercial', 'Industrial', 'Residential'
    subcategory: str          # e.g., 'Conference', 'Warehouse'
    filename: str             # e.g., 'Boat.usd'
    filesize_bytes: int       # File size in bytes
```

### 2.2 Search Query & Result Model (`engine.py`)
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResultItem:
    asset_id: str
    usd_path: str
    thumbnail_path: str
    category: str
    subcategory: str
    filename: str
    score: float              # Cosine similarity in range [0.0, 1.0]
    match_type: str           # "Exact Match" (>=0.85), "High Similarity" (>=0.65), "Semantic Match" (<0.65)

@dataclass
class SearchResponse:
    query_type: str           # "text" | "image"
    query_content: str        # Text prompt string or source image path
    total_results: int
    results: List[SearchResultItem]
```

---

## 3. Module Interfaces

### 3.1 `AssetScanner` (`src/scanner.py`)
```python
class AssetScanner:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def scan(self) -> List[USDAssetRecord]:
        """
        Recursively scans root_dir for *.usd, *.usda, *.usdc files.
        Pairs each asset with its .thumbs/256x256/<name>.usd.auto.png or .png preview.
        Extracts category/subcategory from directory hierarchy.
        """
        ...
```

### 3.2 `SigLIP2Service` (`src/model_service.py`)
```python
import torch
from PIL import Image
import numpy as np

class SigLIP2Service:
    def __init__(self, model_name: str = "google/siglip2-base-patch16-224", device: Optional[str] = None):
        """
        Loads SigLIP 2 model and processor locally.
        Automatically selects CUDA if available, else CPU fallback.
        """
        ...

    def encode_text(self, text: str) -> np.ndarray:
        """
        Computes normalized 768-dim L2-normalized float32 embedding vector.
        """
        ...

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocesses and computes normalized 768-dim L2-normalized float32 embedding vector.
        """
        ...
```

### 3.3 `LocalVectorStore` (`src/vector_store.py`)
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

class LocalVectorStore:
    def __init__(self, storage_path: str = "50_PROJECT/data/qdrant_db", collection_name: str = "usd_assets"):
        """
        Initializes embedded Qdrant client targeting local storage path.
        Creates collection with Cosine distance and 768 dimensions if not exists.
        """
        ...

    def upsert_assets(self, records: List[USDAssetRecord], vectors: np.ndarray) -> int:
        """
        Upserts points with vectors and full payload metadata.
        """
        ...

    def search_vector(self, query_vector: np.ndarray, top_k: int = 10, category_filter: Optional[str] = None) -> List[dict]:
        """
        Executes HNSW similarity search on embedded store.
        """
        ...
```

### 3.4 `SearchEngine` (`src/engine.py`)
```python
class SearchEngine:
    def __init__(self, model_service: SigLIP2Service, vector_store: LocalVectorStore):
        ...

    def search_by_text(self, prompt: str, top_k: int = 10, category: Optional[str] = None) -> SearchResponse:
        ...

    def search_by_image(self, image_path: str, top_k: int = 10, category: Optional[str] = None) -> SearchResponse:
        ...
```

---

## 4. CLI & UI Specification

### 4.1 CLI Commands (`cli.py`)
```bash
# 1. Index or re-index target assets directory into local embedded Qdrant
python src/cli.py index --target "D:\___tmp\USD_assets"

# 2. Search by natural language text query
python src/cli.py search-text "conference table with swivel chairs" --top-k 5

# 3. Search by reference image
python src/cli.py search-image "path/to/reference.png" --category "Commercial"
```

### 4.2 Streamlit Web Interface (`app.py`)
- **Query Inputs**:
  - Text search bar with submit button.
  - Image drag-and-drop file uploader.
  - Sidebar category filter dropdown (`All`, `Commercial`, `Industrial`, `Residential`).
  - Result count slider ($k \in [1, 25]$).
- **Results View**:
  - Grid card presentation: Thumbnail image, asset filename, confidence match badge (`Exact Match` in green, `Similar` in blue), similarity score percentage, and one-click "Copy Path" button.

---

## 5. Traceability Matrix

| Requirement | HLD Component | ADR | EIS Section | Test Category |
|-------------|---------------|-----|-------------|---------------|
| 100% Local Ingestion & Storage | `AssetScanner` & `VectorStore` | ADR-002, ADR-003 | Sec 2.1, 3.1, 3.3 | Unit: `test_scanner.py`, `test_vector_store.py` |
| SigLIP 2 Multimodal Embeddings | `SigLIP2Service` | ADR-001 | Sec 3.2 | Unit: `test_engine.py` |
| Text-to-USD & Image-to-USD Search | `SearchEngine` | ADR-001, ADR-002 | Sec 2.2, 3.4 | Integration: `test_engine.py` |
| Viewpoint Bias & Threshold Tuning | `SearchEngine` & `config.py` | ADR-004 | Sec 2.2, 3.4, 4.2 | Threshold validation in `test_engine.py` |
| Localhost Streamlit & CLI | UI Layer | ADR-002 | Sec 4.1, 4.2 | Smoke / E2E test |

