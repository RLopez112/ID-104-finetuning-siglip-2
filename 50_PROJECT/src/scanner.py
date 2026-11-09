"""USD Asset and Thumbnail Scanner for ID-104."""
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import DEFAULT_USD_DIR, THUMB_EXTENSIONS, USD_EXTENSIONS


@dataclass
class USDAssetRecord:
    """Metadata record for a discovered USD 3D asset."""
    asset_id: str
    usd_path: str
    thumbnail_path: str
    category: str
    subcategory: str
    filename: str
    filesize_bytes: int


class AssetScanner:
    """Recursively traverses USD asset directories and resolves preview images."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else DEFAULT_USD_DIR

    def scan(self) -> List[USDAssetRecord]:
        """
        Scans root_dir recursively for USD assets and pairs them with thumbnails.
        
        Returns:
            List[USDAssetRecord]: List of verified asset records with valid thumbnail paths.
        """
        if not self.root_dir.exists():
            return []

        records: List[USDAssetRecord] = []

        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip hidden thumbnail directories during top-level asset walking
            if ".thumbs" in root_path.parts:
                continue

            for file in files:
                file_path = root_path / file
                ext = file_path.suffix.lower()

                if ext in USD_EXTENSIONS:
                    thumb_path = self._resolve_thumbnail(file_path)
                    if thumb_path and thumb_path.exists():
                        try:
                            rel_parts = file_path.relative_to(self.root_dir).parts
                        except ValueError:
                            rel_parts = file_path.parts
                            
                        category = rel_parts[0] if len(rel_parts) > 1 else "General"
                        subcategory = rel_parts[1] if len(rel_parts) > 2 else "Default"
                        
                        # Generate deterministic canonical UUIDv5 based on absolute path
                        asset_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(file_path.resolve())))
                        filesize = file_path.stat().st_size

                        record = USDAssetRecord(
                            asset_id=asset_id,
                            usd_path=str(file_path.resolve()),
                            thumbnail_path=str(thumb_path.resolve()),
                            category=category,
                            subcategory=subcategory,
                            filename=file,
                            filesize_bytes=filesize,
                        )
                        records.append(record)

        return records

    def _resolve_thumbnail(self, usd_path: Path) -> Optional[Path]:
        """
        Locates the corresponding preview image for a USD file.
        Checks:
        1. .thumbs/256x256/<name>.usd.auto.png
        2. .thumbs/256x256/<name>.usd.png
        3. Same directory: <name>.png, <name>.jpg, etc.
        """
        parent = usd_path.parent
        filename = usd_path.name
        stem = usd_path.stem

        # Omniverse auto thumbnail patterns
        auto_thumb_256 = parent / ".thumbs" / "256x256" / f"{filename}.auto.png"
        if auto_thumb_256.exists():
            return auto_thumb_256

        std_thumb_256 = parent / ".thumbs" / "256x256" / f"{filename}.png"
        if std_thumb_256.exists():
            return std_thumb_256

        # Check sidecar image files in the same directory
        for ext in THUMB_EXTENSIONS:
            sidecar = parent / f"{stem}{ext}"
            if sidecar.exists():
                return sidecar

        return None
