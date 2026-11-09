"""High-Level Search Engine Orchestrator for ID-104."""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from .config import (
    IMAGE_EXACT_THRESHOLD,
    IMAGE_SIMILAR_THRESHOLD,
    TEXT_EXACT_THRESHOLD,
    TEXT_SIMILAR_THRESHOLD,
    TEXT_SEMANTIC_THRESHOLD,
)
from .model_service import SigLIP2Service
from .vector_store import LocalVectorStore


@dataclass
class SearchResultItem:
    asset_id: str
    usd_path: str
    thumbnail_path: str
    category: str
    subcategory: str
    filename: str
    score: float
    match_type: str


@dataclass
class SearchResponse:
    query_type: str
    query_content: str
    total_results: int
    results: List[SearchResultItem]


class SearchEngine:
    def __init__(
        self,
        model_service: SigLIP2Service,
        vector_store: LocalVectorStore,
    ):
        self.model = model_service
        self.store = vector_store

    def search_text(
        self,
        prompt: str,
        top_k: int = 10,
        category: Optional[str] = None,
    ) -> SearchResponse:
        """
        Executes multimodal text-to-USD search.
        """
        query_vector = self.model.encode_text(prompt)
        raw_results = self.store.search(
            query_vector=query_vector,
            top_k=top_k,
            category=category,
        )
        return self._format_response("text", prompt, raw_results)

    def search_image(
        self,
        image_path: str,
        top_k: int = 10,
        category: Optional[str] = None,
    ) -> SearchResponse:
        """
        Executes multimodal image-to-USD search.
        """
        query_vector = self.model.encode_image_path(image_path)
        raw_results = self.store.search(
            query_vector=query_vector,
            top_k=top_k,
            category=category,
        )
        return self._format_response("image", image_path, raw_results)

    def _format_response(
        self,
        query_type: str,
        query_content: str,
        raw_results: List[dict],
    ) -> SearchResponse:
        items: List[SearchResultItem] = []
        for r in raw_results:
            score = r.get("score", 0.0)

            if query_type == "image":
                if score >= IMAGE_EXACT_THRESHOLD:
                    match_type = "Exact Match"
                elif score >= IMAGE_SIMILAR_THRESHOLD:
                    match_type = "High Similarity"
                else:
                    match_type = "Semantic Match"
            else:
                # Text-to-image calibrated thresholds
                if score >= TEXT_EXACT_THRESHOLD:
                    match_type = "Exact Match"
                elif score >= TEXT_SIMILAR_THRESHOLD:
                    match_type = "High Similarity"
                elif score >= TEXT_SEMANTIC_THRESHOLD:
                    match_type = "Semantic Match"
                else:
                    match_type = "Low Relevance"

            items.append(
                SearchResultItem(
                    asset_id=r.get("asset_id", ""),
                    usd_path=r.get("usd_path", ""),
                    thumbnail_path=r.get("thumbnail_path", ""),
                    category=r.get("category", ""),
                    subcategory=r.get("subcategory", ""),
                    filename=r.get("filename", ""),
                    score=round(score, 4),
                    match_type=match_type,
                )
            )

        return SearchResponse(
            query_type=query_type,
            query_content=query_content,
            total_results=len(items),
            results=items,
        )
