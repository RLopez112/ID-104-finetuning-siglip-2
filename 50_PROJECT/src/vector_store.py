"""Embedded Qdrant Vector Store Manager for ID-104."""
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from .config import QDRANT_COLLECTION_NAME, QDRANT_STORAGE_DIR, VECTOR_DIM
from .scanner import USDAssetRecord


class LocalVectorStore:
    """Manages an in-process local Qdrant collection on local workstation disk."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        collection_name: str = QDRANT_COLLECTION_NAME,
        vector_dim: int = VECTOR_DIM,
    ):
        self.storage_path = Path(storage_path) if storage_path else QDRANT_STORAGE_DIR
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.vector_dim = vector_dim

        # In-process embedded Qdrant client targeting local disk
        self.client = QdrantClient(path=str(self.storage_path))
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Creates the target collection with Cosine distance metric if not present."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_records(
        self,
        records: List[USDAssetRecord],
        embeddings: np.ndarray,
    ) -> int:
        """
        Upserts asset records with their corresponding L2-normalized embeddings into Qdrant.
        """
        if len(records) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(records)} records vs {len(embeddings)} embeddings"
            )

        points: List[PointStruct] = []
        for i, record in enumerate(records):
            point = PointStruct(
                id=record.asset_id,
                vector=embeddings[i].tolist(),
                payload={
                    "usd_path": record.usd_path,
                    "thumbnail_path": record.thumbnail_path,
                    "category": record.category,
                    "subcategory": record.subcategory,
                    "filename": record.filename,
                    "filesize_bytes": record.filesize_bytes,
                },
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        return len(points)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs nearest-neighbor search with optional category payload filtering.
        """
        query_filter: Optional[Filter] = None
        if category and category.lower() != "all":
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category),
                    )
                ]
            )

        if query_vector.ndim > 1:
            query_vector = query_vector.squeeze()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            query_filter=query_filter,
            limit=top_k,
        )

        output: List[Dict[str, Any]] = []
        for scored_point in results.points:
            item = dict(scored_point.payload)
            item["asset_id"] = str(scored_point.id)
            item["score"] = float(scored_point.score)
            output.append(item)

        return output

    def count(self) -> int:
        """Returns total vectors indexed in collection."""
        return self.client.count(collection_name=self.collection_name).count

    def clear(self) -> None:
        """Clears collection points."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

