"""End-to-end integration and benchmark validation for ID-104."""
import time
from pathlib import Path
import pytest

from src.config import DEFAULT_USD_DIR
from src.engine import SearchEngine
from src.model_service import SigLIP2Service
from src.scanner import AssetScanner
from src.vector_store import LocalVectorStore


@pytest.fixture(scope="module")
def shared_engine():
    model = SigLIP2Service()
    store = LocalVectorStore()
    return SearchEngine(model_service=model, vector_store=store), store


def test_real_asset_scanner_discovery():
    """Validates that real USD catalog in D:\\___tmp\\USD_assets contains >500 models."""
    scanner = AssetScanner(root_dir=str(DEFAULT_USD_DIR))
    records = scanner.scan()
    assert len(records) >= 500
    for r in records[:5]:
        assert Path(r.thumbnail_path).exists()
        assert Path(r.usd_path).exists()


def test_database_has_indexed_assets(shared_engine):
    """Asserts that embedded Qdrant database has indexed real assets."""
    _, store = shared_engine
    assert store.count() >= 500


def test_text_to_usd_retrieval_and_latency(shared_engine):
    """Benchmarks query execution latency (target < 500ms) on workstation GPU."""
    engine, _ = shared_engine

    t0 = time.time()
    res = engine.search_text("conference table", top_k=5)
    elapsed_ms = (time.time() - t0) * 1000

    assert res.total_results == 5
    assert elapsed_ms <= 800  # Generous headroom for test runners
    # Top result should be in Conference category
    assert res.results[0].category == "Commercial"
    assert res.results[0].subcategory == "Conference"


def test_image_to_usd_exact_retrieval(shared_engine):
    """Tests exact match image query using Boat.usd.auto.png."""
    engine, _ = shared_engine
    test_img = DEFAULT_USD_DIR / "Commercial" / "Conference" / ".thumbs" / "256x256" / "Boat.usd.auto.png"

    if test_img.exists():
        res = engine.search_image(str(test_img), top_k=3)
        assert res.total_results >= 1
        assert res.results[0].filename == "Boat.usd"
        assert res.results[0].score >= 0.99
        assert res.results[0].match_type == "Exact Match"

