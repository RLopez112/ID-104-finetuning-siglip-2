"""Unit tests for LocalVectorStore."""
import shutil
import tempfile
import numpy as np
import pytest

from src.scanner import USDAssetRecord
from src.vector_store import LocalVectorStore


@pytest.fixture
def temp_qdrant_store():
    temp_dir = tempfile.mkdtemp()
    store = LocalVectorStore(storage_path=temp_dir, collection_name="test_collection", vector_dim=4)
    yield store
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_vector_store_upsert_and_search(temp_qdrant_store):
    records = [
        USDAssetRecord(
            asset_id="11111111-1111-1111-1111-111111111111",
            usd_path="D:/test/Asset1.usd",
            thumbnail_path="D:/test/Asset1.png",
            category="Commercial",
            subcategory="Office",
            filename="Asset1.usd",
            filesize_bytes=1024,
        ),
        USDAssetRecord(
            asset_id="22222222-2222-2222-2222-222222222222",
            usd_path="D:/test/Asset2.usd",
            thumbnail_path="D:/test/Asset2.png",
            category="Industrial",
            subcategory="Factory",
            filename="Asset2.usd",
            filesize_bytes=2048,
        ),
    ]

    # Two 4-dim unit vectors
    embeddings = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
    ], dtype=np.float32)

    count = temp_qdrant_store.upsert_records(records, embeddings)
    assert count == 2
    assert temp_qdrant_store.count() == 2

    # Query matching Asset 1 exactly
    query_vector = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    results = temp_qdrant_store.search(query_vector=query_vector, top_k=2)

    assert len(results) == 2
    assert results[0]["asset_id"] == "11111111-1111-1111-1111-111111111111"
    assert results[0]["score"] == pytest.approx(1.0, 1e-4)

    # Filtered search for Industrial
    filtered_results = temp_qdrant_store.search(query_vector=query_vector, top_k=2, category="Industrial")
    assert len(filtered_results) == 1
    assert filtered_results[0]["asset_id"] == "22222222-2222-2222-2222-222222222222"
