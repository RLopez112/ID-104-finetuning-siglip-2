"""Unit tests for AssetScanner."""
import shutil
import tempfile
from pathlib import Path
import pytest

from src.scanner import AssetScanner, USDAssetRecord


@pytest.fixture
def temp_usd_catalog():
    temp_dir = tempfile.mkdtemp()
    base = Path(temp_dir)

    # Mock structure: Commercial/Conference
    conf_dir = base / "Commercial" / "Conference"
    conf_thumbs = conf_dir / ".thumbs" / "256x256"
    conf_thumbs.mkdir(parents=True, exist_ok=True)

    # Asset 1 with auto.png
    (conf_dir / "Desk.usd").write_text("#usda 1.0\n", encoding="utf-8")
    (conf_thumbs / "Desk.usd.auto.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # Asset 2 with standard .png
    (conf_dir / "Chair.usdc").write_text("#usdc 1.0\n", encoding="utf-8")
    (conf_thumbs / "Chair.usdc.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # Asset 3 without thumb (should be ignored by fast-path)
    (conf_dir / "Orphan.usd").write_text("#usda 1.0\n", encoding="utf-8")

    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_scanner_discovers_valid_assets(temp_usd_catalog):
    scanner = AssetScanner(root_dir=temp_usd_catalog)
    records = scanner.scan()

    assert len(records) == 2
    filenames = {r.filename for r in records}
    assert "Desk.usd" in filenames
    assert "Chair.usdc" in filenames
    assert "Orphan.usd" not in filenames

    # Verify category metadata
    for r in records:
        assert r.category == "Commercial"
        assert r.subcategory == "Conference"
        assert Path(r.thumbnail_path).exists()
        assert r.asset_id is not None
        assert r.filesize_bytes > 0


def test_scanner_handles_empty_dir():
    temp_dir = tempfile.mkdtemp()
    scanner = AssetScanner(root_dir=temp_dir)
    records = scanner.scan()
    assert records == []
    shutil.rmtree(temp_dir, ignore_errors=True)
